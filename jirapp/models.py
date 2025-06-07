import json

from django.db import models
from django.conf import settings
from tools.generic_class import GenericClass
from jira import JIRA, JIRAError
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timezone
import inspect
from dateutil import parser
from django.conf import settings

class JiraIssue:

    def __init__(self, connexion, issue, jira_url):
        if settings.DEBUG:
            print("JiraIssue ", inspect.currentframe().f_code.co_name)
        self.con = connexion
        self.issue = issue
        self.jira_url = jira_url
        self.status = self.issue.raw["fields"]["status"]["name"]

    def get_url(self):
        if settings.DEBUG:
            print("JiraIssue ", inspect.currentframe().f_code.co_name)
        return self.jira_url + "browse/" + str(self.issue.key)

    def get_lead_time(self):
        if settings.DEBUG:
            print("JiraIssue ", inspect.currentframe().f_code.co_name)
        created = datetime.strptime(self.issue.fields.created, '%Y-%m-%dT%H:%M:%S.%f%z')
        if self.issue.fields.resolutiondate:
            resolved = datetime.strptime(self.issue.fields.resolutiondate, '%Y-%m-%dT%H:%M:%S.%f%z')
            time = resolved - created
            return time.days
        return None

    def get_cycle_time(self, in_progress_statuses=['In Progress', 'Doing']):
        if settings.DEBUG:
            print("JiraIssue ", inspect.currentframe().f_code.co_name)
        for history in reversed(self.issue.changelog.histories):
            for item in history.items:
                if item.field == "status" and item.toString in in_progress_statuses:
                    started = datetime.strptime(history.created, '%Y-%m-%dT%H:%M:%S.%f%z')
                    if self.issue.fields.resolutiondate:
                        resolved = datetime.strptime(self.issue.fields.resolutiondate, '%Y-%m-%dT%H:%M:%S.%f%z')
                        time = resolved - started
                        return time.days
        return None

    def get_work_item_age(self):
        if settings.DEBUG:
            print("JiraIssue ", inspect.currentframe().f_code.co_name)
        current_status = self.issue.fields.status.name
        transitions = []
        for history in self.issue.changelog.histories:
            for item in history.items:
                if item.field == 'status' and item.toString == current_status:
                    transitions.append(history.created)
        if transitions:
            last_status_change = datetime.strptime(transitions[-1], '%Y-%m-%dT%H:%M:%S.%f%z')
        else:
            last_status_change = datetime.strptime(self.issue.fields.created, '%Y-%m-%dT%H:%M:%S.%f%z')
        age = datetime.now(timezone.utc) - last_status_change
        return age.days

    def get_sprint_added_date(self):
        if settings.DEBUG:
            print("JiraIssue ", inspect.currentframe().f_code.co_name)
        sprint_added_date = None
        for history in self.issue.changelog.histories:
            for item in history.items:
                if item.field == 'Sprint':
                    sprint_added_date = history.created
        return parser.parse(sprint_added_date)

    def get_json(self):
        if settings.DEBUG:
            print("JiraIssue ", inspect.currentframe().f_code.co_name)
        return {'key': self.issue.key,
                'name': self.issue.fields.summary,
                'status': self.status,
                'url': self.get_url(),
                'age': self.get_work_item_age(),
                'cycle_time': self.get_cycle_time(),
                'lead_time': self.get_lead_time(),
                'created': parser.parse(self.issue.fields.created),
                'added': self.get_sprint_added_date()
                }


class JiraSprint:
    issues = []

    def __init__(self, connexion, sprint, jira_url):
        if settings.DEBUG:
            print("JiraSprint ", inspect.currentframe().f_code.co_name)
        self.con = connexion
        self.sprint = sprint
        self.jira_url = jira_url
        self.issues.clear()
        for i in self.con.search_issues(f'sprint = {self.sprint.id}', maxResults=100, expand='changelog'):
            ji = JiraIssue(self.con, i, self.jira_url)
            if ji not in self.issues:
                self.issues.append(ji)

    def get_url(self):
        if settings.DEBUG:
            print("JiraSprint ", inspect.currentframe().f_code.co_name)
        return self.jira_url + "browse/" + str(self.sprint.key)

    def get_issues(self):
        if settings.DEBUG:
            print("JiraSprint ", inspect.currentframe().f_code.co_name)
        return self.issues

    def get_issues_json(self):
        if settings.DEBUG:
            print("JiraSprint ", inspect.currentframe().f_code.co_name)
        return [ji.get_json() for ji in self.get_issues()]

    def get_throughput(self, done_statuses=['Done', 'Closed', 'Resolved']):
        if settings.DEBUG:
            print("JiraSprint ", inspect.currentframe().f_code.co_name)
        return len([ji.issue for ji in self.get_issues() if ji.issue.fields.status.name in done_statuses])

    def get_json(self):
        if settings.DEBUG:
            print("JiraSprint ", inspect.currentframe().f_code.co_name)
        dt = parser.parse(self.sprint.startDate)
        return {'name': self.sprint.name, 'throughput': self.get_throughput(), 'issues': self.get_issues_json(),
                'startDate': parser.parse(self.sprint.startDate), 'endDate': parser.parse(self.sprint.endDate),
                'state': self.sprint.state, 'goal': self.sprint.goal}


class JiraCredential(GenericClass):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jira_credentials')
    name = models.CharField(max_length=255)
    jira_url = models.URLField()
    username = models.CharField(max_length=255)
    api_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    project_key = models.CharField(max_length=255, null=True, blank=True)
    board_id = models.CharField(max_length=255, null=True, blank=True)
    connected = models.BooleanField(default=False)

    verbose_name_plural = _("Jira Credentials")

    def test_connexion(self):
        if settings.DEBUG:
            print("JiraCredential ", inspect.currentframe().f_code.co_name)
        self.con = None
        self.connected = False
        if self.jira_url:
            try:
                self.con = JIRA(server=self.jira_url, basic_auth=(self.username, self.api_token))
                self.connected = True
            except JIRAError:
                self.connected = False

    def __init__(self, *args, **kwargs):
        if settings.DEBUG:
            print("JiraCredential ", inspect.currentframe().f_code.co_name)
        super().__init__(*args, **kwargs)
        self.test_connexion()

    def __str__(self):
        return f"{self.name}"


    def save(self, *args, **kwargs):
        if settings.DEBUG:
            print("JiraCredential ", inspect.currentframe().f_code.co_name)
        is_new = self.pk is None
        self.test_connexion()
        super().save(*args, **kwargs)
        if is_new:
            self.user.jiras.add(self)
            if self.user.current_jira is None:
                self.user.current_jira = self
            self.user.save()

    def get_projects(self):
        if settings.DEBUG:
            print("JiraCredential ", inspect.currentframe().f_code.co_name)
        if self.con:
            return self.con.projects()

    def get_boards(self):
        if settings.DEBUG:
            print("JiraCredential ", inspect.currentframe().f_code.co_name)
        if self.con:
            return self.con.boards(projectKeyOrID=self.project_key)

    def get_sprints(self):
        if settings.DEBUG:
            print("JiraCredential ", inspect.currentframe().f_code.co_name)
        return self.con.sprints(self.board_id)

    def get_active_sprints(self):
        if settings.DEBUG:
            print("JiraCredential ", inspect.currentframe().f_code.co_name)
        sprints = [s for s in self.get_sprints() if s.state == 'active']
        return [JiraSprint(self.con, s, self.jira_url) for s in sprints]

    def get_issues_from_active_sprint(self):
        if settings.DEBUG:
            print("JiraCredential ", inspect.currentframe().f_code.co_name)
        sprints = self.get_active_sprints()
        if len(sprints) != 1:
            print("ERREUR get_issues_from_active_sprint : n sprints > 0")
        return sprints[0].get_issues()

    def get_issues_from_active_sprint_json(self):
        if settings.DEBUG:
            print("JiraCredential ", inspect.currentframe().f_code.co_name)
        return [ji.get_json() for ji in self.get_issues_from_active_sprint()]

    def get_workflow_json(self):
        if settings.DEBUG:
            print("JiraCredential ", inspect.currentframe().f_code.co_name)
        used_statuses = {str(s): {} for s in self.con.statuses()}
        for i, ji in enumerate(self.get_issues_from_active_sprint()):
            used_statuses[ji.status][ji.issue.key] = ji.get_json()
        return used_statuses

    def get_current_sprint_json(self):
        if settings.DEBUG:
            print("JiraCredential ", inspect.currentframe().f_code.co_name)
        return self.get_active_sprints()[0].get_json()
