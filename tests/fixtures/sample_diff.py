"""Sample diffs and file contents for testing agents."""

# A diff with intentional bugs, style issues, and security vulnerabilities
SAMPLE_DIFF = """--- a/app/auth.py
+++ b/app/auth.py
@@ -1,5 +1,25 @@
+import sqlite3
+import os
+import pickle
+
+DB_PASSWORD = "admin123"
+API_KEY = "sk-secret-key-12345"
+
 def login(username, password):
-    pass
+    conn = sqlite3.connect("users.db")
+    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
+    result = conn.execute(query)
+    user = result.fetchone()
+    return user
+
+def get_users(data):
+    users = pickle.loads(data)
+    return users
+
+def get_items(items, index):
+    return items[index]
+
+def process_file(filename):
+    path = "/data/" + filename
+    f = open(path, "r")
+    content = f.read()
+    return content
"""

SAMPLE_FILE_CONTENTS = {
    "app/auth.py": """import sqlite3
import os
import pickle

DB_PASSWORD = "admin123"
API_KEY = "sk-secret-key-12345"

def login(username, password):
    conn = sqlite3.connect("users.db")
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
    result = conn.execute(query)
    user = result.fetchone()
    return user

def get_users(data):
    users = pickle.loads(data)
    return users

def get_items(items, index):
    return items[index]

def process_file(filename):
    path = "/data/" + filename
    f = open(path, "r")
    content = f.read()
    return content
"""
}
