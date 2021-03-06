---
layout: post
title:  "Wordpress and Django: best buddies"
date:   2010-01-17 20:55:29+05:30
categories: about
author: shabda
---
Summary:
How to integrate a non Django database system in your Django code, using Wordpress
as example. [The completed code is available at github](http://github.com/uswaretech/django-wordpress) or you can [see some screnshots](#screenshots_wp)

------------------------------

Though there are quite a [few good](http://github.com/montylounge/django-mingus ) [Django blog](http://byteflow.su/) applications, our blog is based on
[Wordpress](http://wordpress.org/). A [number](http://mitcho.com/code/yarpp/) [of](http://diythemes.com/) [plugin's](http://www.backtype.com/ )
make moving to a Django based app a bad decision
for us, and not in the spirit of "best tools for the job".

We moved the other way, and decided to use [Django to admin the
Wordpress database](http://github.com/uswaretech/django-wordpress). The completed code is available on [Github](http://github.com/uswaretech/django-wordpress)

It is not too hard, with the the builtin Django commands. Django provides the
[`inspectdb`](http://www.djangobook.com/en/1.0/chapter16/) command which allows you to build your models.py from an existing
non Django database.

Here we will see the steps followed for Wordpress, but it would be about the same for all
systems.

##### Take a back up of wordpress


    mysqldump -u wordpress_user -p --database wordpress_database > data.sql

##### Create a new project, and set its settings to use the Wordpress database.


        DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        DATABASE_NAME = ''             # Or path to database file if using sqlite3.
        DATABASE_USER = ''             # Not used with sqlite3.
        DATABASE_PASSWORD = ''         # Not used with sqlite3.
        DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
        DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
    
##### Get the initial models.py


    ./manage.py inspectdb > models.py

This will create all the database tables in a form Django can understand. Here is what this command creates for a
my Wordpress installation with the YARPP plugin. [http://gist.github.com/278962](http://gist.github.com/278962)

##### Create a new app and put this models.py there.


With this done, you can treat the non Django part as a
standalone application. Since Wordpress appends all its table with `wp_` prefix,
we name this applications `wp` to maintain table name compatibility with Django naming
conventions.

You will notice that all models have the `db_table` populated, so we can rename tables, without changes to the database.

##### Differences between Wordpress and Django style naming.


At this point you will notice some differences in how Django names things (in a
best practice sort of way), and how Wordpress does it.

a. Django table and model class name are (generally) singular. eg `class Post(models.Models)` leads to table `app_post`.
Wordpress tables are (most of them) named plural eg `wp_posts`.

b. Django attributes are generally named without the table name part. Eg

    class Comment(models.Model):
        author_name = models.TextField()
        content = models.TextField()

Wordpress is explicit here and includes the table prefix with attributes.
        
    mysql> desc wp_comments;
    +----------------------+---------------------+------+-----+---------------------+----------------+
    | Field                | Type                | Null | Key | Default             | Extra          |
    +----------------------+---------------------+------+-----+---------------------+----------------+
    | comment_ID           | bigint(20) unsigned | NO   | PRI | NULL                | auto_increment | 
    | comment_post_ID      | bigint(20) unsigned | NO   | MUL | 0                   |                | 
    | comment_author       | tinytext            | NO   |     | NULL                |                | 
    | comment_author_email | varchar(100)        | NO   |     |                     |                | 

    .....
    
    
I believe this is due to the way you would generally be using the code. In Django you would do
`comment.author` where being explicit doesn't add any value, while in Wordpress, you would use,
`select comment_author, post_title ... from wp_comment, wp_post ... where join`, where being explicit
is useful.

You can decouple the Django and database names by using the `db_table` and `db_column` attributes.
We choose to rename the Class names to match Django conventions while we let the column names remain the same.

##### Add Admin and other Django niceties.


Wordpress doesn't (seem to) have foreign key constraints setup correctly, and
uses  `bigint(20) unsigned` without foreign key constraints to refer to referred entities.
This means Django creates all ForeignKeys as IntegerFields.

Modify them to use ForeignKey instead. Also add `__unicode__`, to your classes.

Add an `admin.py` to register all your classes. 

And you are done! Now you can access, and work with your Wordpress data inside Django
and Django admin.

----------

There are a few more things which will allow a easier Wordpress setup.

##### Create template tags to show the latest posts and comments.


    @register.inclusion_tag("wp/recent_posts.html")
    def show_posts(num_comments):
        return {"posts": Post.objects.filter(post_type="post", post_status="publish").order_by("-post_date")[:num_comments]}

So you can see that there is nothing Wordpress specific we need too do here.

##### Create a better admin.


    Add ModelAdmin to generally used models.
    
##### Allows accessing attributes via the Django style names.


If you override `__getattr__`, you can access
the attributes via other names. Eg in the current setup you need to do `comment.comment_content`, `comment.comment_author` etc,
while we would like to do `comment.content`  and `comment.author` as a shortcut.
    
    class WordPressModel(object):    
        def __getattr__(self, v):
            if v in self.__dict__:
                return self.__dict__[v]
            else:
                new_v = "%s_%s" % (self.__class__.__name__.lower(),  v)
                if new_v in self.__dict__:
                    return self.__dict__[new_v]
                else:
                    raise AttributeError

It is highly debatable whether this is a good idea :), but it is too convenient right now not to test this method out.

<a name="screenshots_wp" />
Here are some screenshots.

<img alt="" src="http://uswaretech.com/dump/screenshots/screenshot_010.png" title="Wordpress django admin" class="alignnone" width="600" />

<img alt="" src="http://uswaretech.com/dump/screenshots/screenshot_011.png" title="Wordpress django admin" class="alignnone" width="600" />



----------------------------
[Do you subscribe to our feed](http://feeds.feedburner.com/uswarearticles)? We recently made a full text feed available, so if you are using the old feed, you should change it. [Subscribe now](http://feeds.feedburner.com/uswarearticles).

