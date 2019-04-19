import urllib
import json
import re
import csv
import codecs
import sys
import time
import requests
import imdb
from imp import reload
import re
import os
import pandas
from imdb import IMDb
from imdbpie import Imdb
import math

from imdb.utils import analyze_name, canonicalName, normalizeName, \
                        analyze_title, date_and_notes

LA_COUNTRIES=re.compile(".*Cuba.*|.*Dominican Republic.*|.*Puerto Rico.*|.*Costa Rica.*|.*El Salvador.*|.*Guatemala.*|.*Mexico.*|.*Nicaragua.*|.*Panama.*|.*Argentina.*|.*Nicaragua.*|.*Bolivia.*|.*Chile.*|.*Colombia.*|.*Ecuador.*|.*Guyana.*|.*Paraguay.*|.*Peru.*|.*Uruguay.*|.*Venezuela.*")
LA_NAMES=re.compile(".*ez$|.*do$|.*ro$")
#CREW_INFO=re.compile(".*music.*|.*production design.*|.*crew.*|.*department.*|.*make up.*|.*designer.*|.*production manager.*|.*producer.*|.*cinematographer.*|.*direct.*|.*stunt performer.*|.*set decoration.*|.*writer.*|.*editor.*|.*visual.*")
CREW_INFO=re.compile(".*producer.*|^director|.*writer.*")
f=open('Comedy'+str(2009)+'Cast.csv', 'w')
g=open('Comedy'+str(2009)+'Crew.csv','w')

def persondetails(presult,pid,typeperson):
	p_result = ia.search_person(presult)
	listcsv=list()
	for item in p_result:
		if(str(item.personID)==str(pid)):
			listkeyvalue=dict()
			print("------------------------------")
			print("Actor")
			print(item['long imdb canonical name'],item['name'])
			ia.update(item)
			print(item.keys())
			if 'mini biography' in item.keys():
				print("mini biography")
				print(item['mini biography'])
			if 'birth notes' in item.keys():
				listkeyvalue[item['canonical name'].encode('utf-8')]=item['birth notes'].encode('utf-8')
				#print type(item['birth notes'])
				print("birth notes")
				print(item['birth notes'])
				try:
					flag=0
					if typeperson=="cast":
						f.write(";"+str(item['birth notes'].encode('utf-8','ignore')))
					else:
						g.write(";"+str(item['birth notes']))
					if LA_COUNTRIES.findall(str(item['birth notes'].encode('utf-8','ignore'))):
						if typeperson=="cast":
							f.write(";Latinx")
						else:
							g.write(";Latinx")
						flag=1
					if LA_NAMES.findall(str(item['long imdb canonical name'].encode('utf-8','ignore'))):
						if flag==0:

							if typeperson=="cast":
								f.write(";Latinx")
							else:
								g.write(";Latinx")

				except UnicodeEncodeError as ude:
					if typeperson=="cast": 
						#f.write(";error")
						continue
					else:
						#g.write(";error")
						continue

			if listkeyvalue:
				listcsv.append(listkeyvalue)
		
			print("--------------------------------")

ia = imdb.IMDb() # by default access the web.
in_encoding = sys.stdin.encoding or sys.getdefaultencoding()
out_encoding = sys.stdout.encoding or sys.getdefaultencoding()
i = IMDb()
#imdbcast=open('imdbcast.csv','w')
#imdbcrew=open('imdbcrew.csv','w')

def moviedetails(sresult,seasonnum):
	imdbp = Imdb()
	
	tv_result = ia.search_movie(sresult)
	
	print("sresult",sresult,tv_result)
	
	


	for item in tv_result:


		print("--------MOVIE DETAILS IMDB---------------")
		#print(type(item))
		i.update(item)
		#print(item)
		print(item['long imdb title'], item.movieID)
		#print(ia.get_movie[item.movieID])
		print(sresult)
		print((item['long imdb title']))
		#ia.update(item)
		try:
			m=imdbp.get_title_episodes(str("tt"+item.movieID))
		except:
			continue
		#m=(i.get_movie(item.movieID))
		print("ID FOR TV and SEASON",m,seasonnum)
		
		if m==None or math.isnan(seasonnum):
			continue
		print("Updating episodes")
		seasonnum = int(seasonnum)-1
		g.write(str(sresult)+";"+str(seasonnum+1))
		g.write("\n")
		try:
			#print(item['long imdb title'])
			print("______________EPISODES_______________\n")
			#print(m['episodes'])
			#for t in m['seasons'][seasonnum]:
			if 'seasons' in  m.keys():
				if 'episodes' in m['seasons'][seasonnum].keys():
					for u in range(0,len(m['seasons'][seasonnum]['episodes'])):
						e = m['seasons'][seasonnum]['episodes'][u]['title']
						g.write("\n")
						g.write(str(e)+"%")
						g.write("\n")
						print(str(e))
						match = re.search('/title/(.*)/',m['seasons'][seasonnum]['episodes'][u]['id'])
						titleid = match.group(1)
						#i.update(e)
						#details = i.get_movie(e.movieID)
						#i.update(details,'all')
						#print("DETAILS KEYS",details.keys())
						#x = i.get_movie_infoset()
						#print("INFOSET",x)
						#print("MOVIE WRITER",details['writer'])
						#print("MOVIE DIRECTOR",details['director'])
						print("MOVIE ID",titleid)
						persondetail = imdbp.get_title_credits(str(titleid))
						if 'writer' in persondetail['credits'].keys():
							for index, item in enumerate(persondetail['credits']['writer']):
								#if persondetail['credits']['writer'][index]['job']=='written by':
								if 'job' in persondetail['credits']['writer'][index].keys():
									g.write(str(persondetail['credits']['writer'][index]['name'])+";"+str(persondetail['credits']['writer'][index]['job']))
								else:
									g.write(str(persondetail['credits']['writer'][index]['name'])+";"+"writer")
								match = re.search('/name/nm(.*)/',persondetail['credits']['writer'][index]['id'])
								idofactor = match.group(1)
								persondetails(str(persondetail['credits']['writer'][index]['name']),idofactor,'crew')
								g.write("\n")
						if 'director' in persondetail['credits'].keys():
							for index, item in enumerate(persondetail['credits']['director']):
								if persondetail['credits']['director'][index]['category']=='director':
									
									g.write(str(persondetail['credits']['director'][index]['name'])+";"+"director")
									match = re.search('/name/nm(.*)/',persondetail['credits']['director'][index]['id'])
									idofactor = match.group(1)
									persondetails(str(persondetail['credits']['director'][index]['name']),idofactor,'crew')
									g.write("\n")
						if 'producer' in persondetail['credits'].keys():
							for index, item in enumerate(persondetail['credits']['producer']):
								#if persondetail['credits']['producer'][index]['job']=='producer' or persondetail['credits']['producer'][index]['job']=='executive producer':
								if 'job'in persondetail['credits']['producer'][index].keys():
									g.write(str(persondetail['credits']['producer'][index]['name'])+";"+str(persondetail['credits']['producer'][index]['job']))
								else:
									g.write(str(persondetail['credits']['producer'][index]['name'])+";"+"producer")
								match = re.search('/name/nm(.*)/',persondetail['credits']['producer'][index]['id'])
								idofactor = match.group(1)
								persondetails(str(persondetail['credits']['producer'][index]['name']),idofactor,'crew')
								g.write("\n")
							

						#break

			print("_______END EPISODES___________\n")
			
		except UnicodeEncodeError as ude:
			continue
				
			#ia.update(item,'all')
			#ia.update(item,'trivia')
			#print(item['trivia'])
	#sys.setdefaultencoding('utf8')

reload(sys)





#sys.setdefaultencoding('utf8')
imdbpylist=list()
def getmoviesbyyear():
	global f
	global g
	listyear = [1956]

	for j in listyear:

		#uncomment for reading from excel
		df = pandas.read_excel(str(j)+'.xlsx',sheetname='Sheet1')
		
		#uncomment for reading from excel
		values = df['Top 10 Comedy TV Shows'].values
		values=values.tolist()
		values2 = df['Season'].values
		values2 = values2.tolist()

		#values = eval(values)
		#For unicode uncomment below
		#values = [str(x.replace(u'\xa0', u' ').encode('utf-8','ignore')[1:]) for x in values]
		#print values
		#imdbpylist=["Modern Family"]
		#imdbpylist=["Annie Get Your Gun (1950)","Fancy Pants (1950)","Cheaper by the Dozen (1950)","Harvey (1950)","Father of the Bride (1950)","Never a Dull Moment (1950)","For Heaven's Sake (1950)","Key to the City (1950)","Born Yesterday (1950)","Three Little Words (1950)","At War with the Army (1950)","Tea for Two (1950)", "Francis (1950)","Last Holiday (1950)","Tapahtui kaukana (1950)","The Jackpot (1950)","A Ticket to Tomahawk (1950)","Two Weeks with Love (1950)","The Happiest Days of Your Life (1950)","Borderline (1950)","Nancy Goes to Rio (1950)","Beauty and the Devil (1950)","The West Point Story (1950)","The Happy Years (1950)","The Admiral Was a Lady (1950)","My Friend Irma Goes West (1950)","Let's Dance (1950)","Three Husbands (1950)","Abbott and Costello in the Foreign Legion (1950)", "Louisa (1950)", "When Willie Comes Marching Home (1950)","Mrs. O'Malley and Mr. Malone (1950)","Father Is a Bachelor (1950)", "What the Butler Saw (1950)"]
		#mdbpylist=["A Ticket to Tomahawk (1950)","Two Weeks with Love (1950)","The Happiest Days of Your Life (1950)","Borderline (1950)","Nancy Goes to Rio (1950)","Beauty and the Devil (1950)","The West Point Story (1950)","The Happy Years (1950)","The Admiral Was a Lady (1950)","My Friend Irma Goes West (1950)","Let's Dance (1950)","Three Husbands (1950)","Abbott and Costello in the Foreign Legion (1950)", "Louisa (1950)", "When Willie Comes Marching Home (1950)","Mrs. O'Malley and Mr. Malone (1950)","Father Is a Bachelor (1950)", "What the Butler Saw (1950)"]
		#imdbpylist=["Annie Get Your Gun (1950)","Fancy Pants (1950)","Cheaper by the Dozen (1950)","Harvey (1950)","Father of the Bride (1950)","Never a Dull Moment (1950)","For Heaven's Sake (1950)","Key to the City (1950)","Born Yesterday (1950)","Three Little Words (1950)","At War with the Army (1950)","Tea for Two (1950)", "Francis (1950)","Last Holiday (1950)","Tapahtui kaukana (1950)","The Jackpot (1950)""]
		#imdbpylist=["Kotch (1971)"]
		#imdbpylist=["Steptoe and Son (1972)","Teenage Playmates (1974)"]
		#imdbpylist=["Moonrunners (1975)","White Collar Blues (1975)"]
		imdbpylist=values

		#imdbpylist=["Two or Three Things I Know About Her... (1967)"]
		#imdbpylist=["What Did You Do in the War, Daddy? (1966)","Way... Way Out (1966)","The Olsen Gang (1968)","Don't Raise the Bridge, Lower the River (1968)","Here We Go Round the Mulberry Bush (1968)","Lions Love (... abd Lies) (1969)","The Secret Sex Lives of Romeo and Juliet (1969)","If It's Tuesday, This Must Be Belgium (1969)"]
		#imdbpylist=["Abbott and Costello Meet the Mummy (1955)","The Adventures of Huckleberry Finn (1960)","Snow White and the Three Stooges (1961)","The Outrageous Baron Munchausen (1962)","The Knack and How to Get It (1965)","John Goldfarb, Please Come Home!(1965)","Bela Lugosi Meets a Brooklyn Gorilla (1952)"]
		#imdbpylist=["Annie Get Your Gun (1950)"]
		#imdbpylist=["Lady and the Tramp (1995)","Mister Roberts (1995)","The Tender Trap (1995)","The Seven Year Itch (1995)","Guys and Dolls (1995)","Oklahoma! (1995)","The Court Jester","The Trouble with Harry (1995)","The Ladykiller (1995)","To Paris with Love Sissi (1995)","Abbott and Costello Meet the Mummy (1995)","We're No Angels (1995)","A Kid for Two Farthings (1995)","Smiles of a Summer Night (1995)","The Long Gray Line (1995)","The Rose Tattoo (1995)","Orders Are Orders (1995)","Il Bidone (1995)","Make Me an Offer (1995)","It's Always Fair Weather (1995)","Hit the Deck (1995)","My Sister Eileen (1995)","Artists and Models (1995)","Shree 420 (1995)","The Private War of Major Benson (1995)","You're Never Too Young (1995)","The Seven Little Foys (1995)","Francis in the Navy (1995)","Gentlemen Marry Brunettes (1995)","Scandal in Sorrento (1995)"]
		for ind,i in enumerate(imdbpylist):
			#f=open('Seasonnew'+str(j)+'temp6Cast.csv', 'w')
			print("NEXT MOVIE")
			g=open(str(i)+"_"+str(values2[ind])+'_Crew.csv','w')
			moviedetails(i,values2[ind])

	
def main():
	getmoviesbyyear()

if __name__ == '__main__':
	main()
	