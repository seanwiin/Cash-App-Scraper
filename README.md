Goal
-------------
Send a webhook of any future upcoming Cash App sweepstakes. Typically a sweepstake occurs randomly from the Cash App Twitter profile but with this script, you'll be able to find out before the sweepstakes occurs.  
<br>
From the example below, this sweepstakes went live on February 7, 2023 at 11:31AM PST. And if you look at the image below it, you can see our script was able to locate this backend sweepstakes on February 3, 2023 at 10:41AM PST, 4 days earlier! 

<br>

![cashapp_git](https://user-images.githubusercontent.com/17304842/220838458-2303fd84-264b-44aa-8d3c-9b36b39f1bc3.JPG)

<br>

![cashapp_git2](https://user-images.githubusercontent.com/17304842/220838906-ee9d865b-8120-4542-908c-8bf473d55f5c.JPG)


How does it work?
-------------

This is a script that locates any new changes on the Cash App Sitemap and sends a webhook notification to a Discord Channel. The script can identify a sweepstake event timestamp (if applicable) and send a notification if it occurs. 

How To Use This
---------------
1. Copy the code to your local machine.
2. Insert the `mySQL credentials` and `Discord webhook information`.
3. Create a table called `cashapp` in your mySQL environment and add the following fields. 

```
CREATE TABLE cashapp (
  id int AUTO_INCREMENT PRIMARY KEY,
  rules_title varchar(100),
  user_title  varchar(100),
  unix_timestamp varchar(50),
  event_timestamp datetime,
  created_at datetime,
)
```
4. Run `cashapp.py`
