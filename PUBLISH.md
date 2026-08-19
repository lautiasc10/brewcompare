# Publishing BrewCompare to GitHub Pages (free)

About three minutes of clicking. No commands, no software to install. At the end you
get a public URL like `https://yourname.github.io/brewcompare/` — that's the URL you
paste into the Amazon Associates application form.

---

## 1. Get a GitHub account

Go to **github.com** and sign up if you don't have an account. It's free and takes a
minute. Any email works.

## 2. Create the repository

1. Click the **+** in the top right → **New repository**.
2. **Repository name:** `brewcompare`
3. Set it to **Public**. (Pages only works on public repos on the free plan, and a
   public repo is what you want anyway — Amazon needs to be able to see the site.)
4. Leave every checkbox unticked — no README, no .gitignore, no license.
5. Click **Create repository**.

## 3. Upload the files

On the empty repository page, click the link that says
**"uploading an existing file"**.

Now — this is the part to get right — unzip the `brewcompare.zip` you were sent, open
the resulting `brewcompare` folder, and **select everything inside it** (all the .html
files, `styles.css`, `main.js`, and the `assets`, `lib`, `datos` and `tools` folders).
Drag that selection onto the GitHub upload area.

> **Do not drag the `brewcompare` folder itself.** `index.html` has to sit at the top
> level of the repository. If you upload the folder, everything ends up one level too
> deep and the site won't load.

Wait for the uploads to finish, then click **Commit changes** at the bottom.

## 4. Turn on GitHub Pages

1. In the repository, click **Settings** (top bar).
2. In the left sidebar, click **Pages**.
3. Under **Build and deployment → Source**, choose **Deploy from a branch**.
4. Set **Branch** to `main` and the folder to `/ (root)`. Click **Save**.

## 5. Wait, then open it

GitHub takes **30 seconds to 2 minutes** to build the site the first time. Refresh the
Pages settings screen; when it's ready a green box appears at the top with your live
URL:

```
https://<your-github-username>.github.io/brewcompare/
```

If you get a 404 at first, that's normal — it's still building. Wait a minute and
refresh.

**That URL is what goes in the Amazon Associates application.**

---

## Updating the site later

Two ways:

**The easy way (browser):** in the repository, click **Add file → Upload files** and
drag in the changed files. They overwrite the old ones. GitHub rebuilds automatically
in about a minute.

**The proper way:** send me the updated folder and I'll tell you exactly which files
changed, or connect the repository and I'll push the changes directly.

---

## Notes for the Amazon Associates application

- The affiliate disclosure Amazon requires is already on every page: in the bar at the
  top, in a box at the bottom, in the footer, and on its own page at
  `/affiliate-disclosure.html`. Reviewers do check for this.
- The site currently ships with three real machines and a **placeholder affiliate tag**
  (`YOURTAG-20`). That's fine for the application — Amazon wants to see a real,
  functioning site with genuine content, which this is. Once your account is approved
  and you have your real tag, send it to me and I'll rebuild every buy button with it.
- The yellow "sample catalogue" banner at the top of the site disappears automatically
  once the real tag is set. You may want it gone before you submit the application —
  tell me and I'll turn it off.
