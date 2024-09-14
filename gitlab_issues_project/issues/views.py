import requests
from django.conf import settings
from django.shortcuts import render
from collections import defaultdict

def issue_board(request):
    # Fetch issues
    issues_url = f"{settings.GITLAB_URL}/api/v4/projects/{settings.GITLAB_PROJECT_ID}/issues"
    headers = {'PRIVATE-TOKEN': settings.GITLAB_ACCESS_TOKEN}
    params = {'per_page': 100, 'scope': 'all'}
    
    response = requests.get(issues_url, headers=headers, params=params)
    issues = response.json()

    # Fetch project members
    members_url = f"{settings.GITLAB_URL}/api/v4/projects/{settings.GITLAB_PROJECT_ID}/members/all"
    response = requests.get(members_url, headers=headers)
    members = response.json()

    # Process issue statistics and group issues by user
    user_issue_count = defaultdict(int)
    user_issues = defaultdict(list)
    for issue in issues:
        author = issue['author']['username']
        user_issue_count[author] += 1
        assignees = issue.get('assignees', [])
        if assignees:
            for assignee in assignees:
                user_issues[assignee['username']].append(issue)
        else:
            user_issues[author].append(issue)

    # Prepare data for the chart
    chart_data = {
        'labels': [],
        'data': []
    }

    # Prepare data for the board
    board_data = []
    for member in members:
        username = member['username']
        chart_data['labels'].append(username)
        chart_data['data'].append(user_issue_count.get(username, 0))
        board_data.append({
            'username': username,
            'name': member['name'],
            'avatar_url': member['avatar_url'],
            'issues': user_issues.get(username, [])
        })

    return render(request, 'issues/issue_board.html', {
        'board_data': board_data,
        'chart_data': chart_data,
    })