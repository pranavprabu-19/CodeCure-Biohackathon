Pushing your code to GitHub is a fundamental skill, but it can feel a bit like a magic spell the first few times you do it. 

Here is the straightforward, step-by-step process to get your local files onto GitHub.

### Step 1: Initialize Git in your project folder
If you haven't already turned your project folder into a Git repository, you need to do that first. Open your terminal (or command prompt), navigate to your project folder, and run:
```bash
git init
```
*This tells Git to start tracking the files in this folder.*

### Step 2: Stage and Commit your files
Next, you need to tell Git which files you want to save, and then actually save them with a message describing what you did.

1. **Stage all files:**
   ```bash
   git add .
   ```
   *(The `.` means "add everything in this folder". If you only want to add a specific file, use `git add filename.py`)*

2. **Commit the files:**
   ```bash
   git commit -m "Initial commit"
   ```
   *(The message inside the quotes should briefly describe the changes. "Initial commit" is standard for the first push.)*

### Step 3: Create a Repository on GitHub
1. Go to [GitHub.com](https://github.com) and log in.
2. Click the **"+"** icon in the top right corner and select **New repository**.
3. Give your repository a name (e.g., `my-awesome-project`).
4. Leave it as Public or Private, and **do not** check the boxes to add a README, .gitignore, or license right now (it's easier to push existing code to an empty repo).
5. Click **Create repository**.

### Step 4: Link your local folder to GitHub and Push
After creating the repo, GitHub will show you a page with some commands. Look for the section titled **"…or push an existing repository from the command line"**.

Copy and paste those exact three lines into your terminal. They will look like this:

1. **Rename your main branch to 'main'** (the modern standard):
   ```bash
   git branch -M main
   ```
2. **Link your local repo to the GitHub URL:**
   ```bash
   git remote add origin https://github.com/YourUsername/YourRepoName.git
   ```
3. **Push the code to GitHub:**
   ```bash
   git push -u origin main
   ```

### How to push changes later on
Once you've done the initial setup above, pushing future updates is much faster. You only need these three commands whenever you change your files:

```bash
git add .
git commit -m "Added a new feature"
git push
```

