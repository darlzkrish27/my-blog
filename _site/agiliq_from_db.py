#!/usr/bin/python
import os
import datetime
hostname = 'localhost'
username = 'postgres'
password = 'root'
database = 'agiliq_blog'


def doQuery( conn ) :
	cur = conn.cursor()

	cur.execute( "SELECT b.text_markup_type, b.title, b.created_on, b.publish_date, b.slug, b.summary, a.username, t.name, b.text FROM blogango_blogentry as b, auth_user as a, taggit_tag as t , taggit_taggeditem as ti WHERE a.id = b.created_by_id AND t.id = ti.tag_id AND ti.object_id = b.id;" )
	for text_markup_type, title, created_on, publish_date, slug, summary,authors,tags, text in cur.fetchall() :
		if text_markup_type =='markdown':
			file = open(os.path.join("_posts",str(publish_date.date())+"-"+slug+".markdown"),"w")
			file.write("---"+"\n")
			file.write("layout: "+"post"+"\n")
			file.write("title:  "+ '"'+title+'"'+"\n")
			file.write("date:   "+ str(publish_date)+"\n")
			file.write("categories: "+ tags+"\n")
			file.write("author: "+ authors+"\n")
			file.write("---"+"\n")

			# file.write("Slug: "+ slug+"\n")
			
			
			# file.write("Summary: "+ summary+"\n")
			file.write(text+"\n")
			file.write("\n")
		# if text_markup_type == 'restructuredtext':
		# 	file = open(os.path.join("content/rst",slug+".rst"),"w")
		# 	file.write(title+"\n")
		# 	for i in title:
		# 		file.write("#")
		# 	file.write("\n"+":date: "+ str(created_on)+"\n")
		# 	file.write(":modified: "+ str(publish_date)+"\n")
		# 	file.write(":slug: "+ slug+"\n")
		# 	file.write(":authors: "+ authors+"\n")
		# 	file.write(":tags: "+ tags+"\n")
		# 	file.write(":summary: "+ summary+"\n")
		# 	file.write("\n"+str(text)+"\n")
		# 	file.write("\n")
		# if text_markup_type =='html':
		# 	file = open(os.path.join("content/html",slug+".html"),"w")
		# 	file.write("<html><head><title>"+title+"</title>"+"\n")
		# 	file.write("<meta name="+'"'+"tags"+'"'+" content="+'"'+tags+'"'+"/>")
		# 	file.write("<meta name="+'"'+"date"+'"'+" content="+'"'+str(created_on)+'"'+"/>")
		# 	file.write("<meta name="+'"'+"modified"+'"'+" content="+'"'+str(publish_date)+'"'+" />")
		# 	file.write("<meta name="+'"'+"authors"+'"'+" content="+'"'+authors+'"'+"/>")
		# 	file.write("<meta name="+'"'+"summary"+'"'+" content="+'"'+summary+'"' +"/>"+"\n")
		# 	file.write("<body>"+text+"</body>"+"\n")
		# 	file.write("</html>"+"\n")

import psycopg2
myConnection = psycopg2.connect( host=hostname, user=username, password=password, dbname=database )
doQuery( myConnection )
myConnection.close()
