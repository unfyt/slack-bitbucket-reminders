import re
from urllib.request import HTTPBasicAuthHandler
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv
load_dotenv()

# Define the API passwords through the .env file 
BITBUCKETUSERNAME = os.getenv('BITBUCKETUSERNAME')
BITBUCKETAPPPASSWORD = os.getenv('BITBUCKETAPPPASSWORD')
SLACKAPIKEY = os.getenv('SLACKAPIKEY')
REMINDERTIME = os.getenv('REMINDERTIME')

class BitBucket():
    headers = {"Accept": "application/json"}

    def __init__(self) -> None:
        self.auth = HTTPBasicAuth(BITBUCKETUSERNAME, BITBUCKETAPPPASSWORD)
    
    def getRepositories(self):
        url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKETUSERNAME}"
        response = requests.get(url, BitBucket.headers, auth = self.auth).json()
        
        repositories = []
        for repo in response["values"]:
            repositories.append(repo["slug"])
        return repositories

    def getPullRequests(self, repository = None):
        if repository: 
            url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKETUSERNAME}/{repository}/pullrequests/"
            response = requests.get(url, BitBucket.headers, auth = self.auth).json()
            return response["values"]

    def getPullRequestComments(self, repository = None, pullrequestid = None):
        if (pullrequestid and repository):
            url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKETUSERNAME}/{repository}/pullrequests/{pullrequestid}/comments"
            response = requests.get(url, BitBucket.headers, auth = self.auth).json()
            comments = []
            for comment in response["values"]:
                comments.append(comment)
            return comments

def getUnansweredComments():

    bitbucket = BitBucket()
    unansweredcomments = []
    # Get a list of all repositories
    repositories = bitbucket.getRepositories()

    # Get all pull requests from repositories
    pullrequests = []
    for repository in repositories:
        pullrequest = bitbucket.getPullRequests(repository=repository)
        for result in pullrequest:
            pullrequests.append(result)

    # Get all comments from pull requests
    comments = []
    for pullrequest in pullrequests:
        if int(pullrequest["comment_count"]) > 0:
            pullrequestcomments = bitbucket.getPullRequestComments(repository=pullrequest["source"]["repository"]["name"], pullrequestid=pullrequest["id"])
            for pullrequestcomment in pullrequestcomments:
                comments.append(pullrequestcomment)

    for comment in comments:
        if "@" in comment["content"]["html"]: # If the comment mentions someone
                x = re.search("(?<=@)(.*)(?=<\/span)", comment["content"]["html"]) # Regex to search for who they mentioned, returns match
                print(f"Comment tagged: {x[1]}")
                replies = list(item for item in comments if "parent" in item and 
                    item["parent"]["id"] == comment['id'] and 
                    item["user"]["display_name"] == x[1]) # Creates a list of replies to this comment if they match the tagged users name
                
                if (len(replies) == 0): # If no replies are found that match the tagged users name
                    commentlink = comment["links"]["html"]["href"]
                    unansweredcomments.append({"user" : x[1], "link": commentlink})
                    print(f"{x[1]} has an unanswered pull request comment in {commentlink}.")

    return unansweredcomments

unansweredcomments = getUnansweredComments()
print(unansweredcomments)