"""
Converts posts of a given Stack Exchange forum to text transcript so can be 
read by a text to voice reader, e.g. using phone while on the go. 
Is good for Stack Exchange forums that are not highly visual 
(e.g. Physics is highly visual with images and equations, but Puzzles, 
Role Playing Games, etc. are mostly text and are well suited to voice reading.)

Is a text transcript, so obviously ignores images, etc. that are included in posts.
Intended use is for forums that have mostly text only content, not images or formulas.


1. Visit Stack Exchange Data Dump and download desired topic as a 7Z archive:
https://archive.org/details/stackexchange
Click on 7Z Files on right side of page (e.g. puzzling)

2. Specify some path names in script below

3. Will output a .txt file transcript of posts and comments for given forum:
Stack_Exchange_Transcript_Output_{timestamp}
Between extracting 7Z archive and parsing xml, may take few mins to complete.

4. Use your favorite text-to-speech app, e.g. for Android:
@Voice Read Aloud by Hyperionics Technology LLC




*Assumes you have 7zip installed, or have 7zip portable on your computer:
http://portableapps.com/apps/utilities/7-zip_portable

**Assumes you have Python xml library called "xmltodict":
C:\Users\Me>pip install xmltodict
C:\Users\Me>pip list

Working fine on:
Python 2.7.8 |Anaconda 2.3.0 (64-bit)| (default, Jul  2 2014, 15:12:11) [MSC v.1500 64 bit (AMD64)] on win32
"""


import xmltodict
import subprocess
import os
import time
import re

#==============================================================================
#Path names to specify:
folder_path_of_7zip_exe = r"C:\MY PROGRAMS\7-ZipPortable\App\7-Zip64" #Path to the folder containing 7z application file
path_to_archive = r"C:\Users\Grey\Desktop\puzzling.stackexchange.com.7z" #path of the 7Z archive you just downloaded
outer_save_dir = r"C:\Users\Grey\Desktop"
#==============================================================================











#==============================================================================
# Leave below as is
#==============================================================================


#Make save path which has timestamp in name so won't overwrite, and so know when last downloaded Stack Exchange data:
timestamp = time.strftime('%Y_%m_%d__%H_%M_%S',time.localtime(time.time()))
output_dir = os.path.join(outer_save_dir,"Stack_Exchange_Transcript_Output_{}".format(timestamp))
os.mkdir(output_dir)
transcript_dir = os.path.join(output_dir,'Transcripts')
os.mkdir(transcript_dir)
utf_encode = 'utf8'


#Extract the 7z archive:
print "Extracting the 7z archive..."
subprocess.call([os.path.join(folder_path_of_7zip_exe,'7z'), 'x', '-o{}'.format(output_dir), path_to_archive], shell=False)
print "\n\n\n\n\nFinished extracting the 7z archive"



#Parse the Posts xml file
print '\n\n\n\n\nParsing xml files...'
with open(os.path.join(output_dir,'Posts.xml'),"r") as ff:
    posts_xml = xmltodict.parse(ff)
Nposts = len(posts_xml['posts']['row'])

#Parse the Comments xml file
with open(os.path.join(output_dir,'Comments.xml'),"r") as gg:
    comments_xml = xmltodict.parse(gg)    
Ncomments = len(comments_xml['comments']['row'])



#Get list of IDs for main posts:    
main_post_IDs_list = []
main_post_inds_list = []
for ii in xrange(Nposts):
    pp = posts_xml['posts']['row'][ii]
    if pp['@PostTypeId'] == '1':
        main_post_IDs_list += [pp['@Id']]
        main_post_inds_list += [ii]
max_main_post_ID = main_post_IDs_list[-1]


#For each of the main posts, get the associated responses and comments and make into a large string:
for cnt, post_ID in enumerate(main_post_IDs_list):
    
    print 'post_ID', post_ID, 'of ', max_main_post_ID
    
    #Get main question:
    string = u'START STACK EXCHANGE QUESTION: ID {}\n'.format(post_ID)
    string += 'Title: ' + posts_xml['posts']['row'][main_post_inds_list[cnt]]['@Title'] + '\n'
    string += 'Body: ' + posts_xml['posts']['row'][main_post_inds_list[cnt]]['@Body'] + '\n'
    #Add comments on original post:
    op_comments = [comments_xml['comments']['row'][mm]['@Text'] for mm in xrange(Ncomments) if comments_xml['comments']['row'][mm]['@PostId']==post_ID]
    for OPcomment in xrange(len(op_comments)):
        string += u'OP COMMENT {0}: {1}\n'.format(str(OPcomment+1),op_comments[OPcomment])

    #Now get other posts and their associated comments:
    response_posts_ID_list = [posts_xml['posts']['row'][jj]['@Id'] for jj in xrange(Nposts) if posts_xml['posts']['row'][jj]['@PostTypeId']=='2' and posts_xml['posts']['row'][jj]['@ParentId']==post_ID]
    response_posts_body_list = [posts_xml['posts']['row'][jj]['@Body'] for jj in xrange(Nposts) if posts_xml['posts']['row'][jj]['@PostTypeId']=='2' and posts_xml['posts']['row'][jj]['@ParentId']==post_ID]
    Nresponses = len(response_posts_ID_list)
    
    for nn in xrange(Nresponses):
        resp_comments_list = [comments_xml['comments']['row'][mm]['@Text'] for mm in xrange(Ncomments) if comments_xml['comments']['row'][mm]['@PostId']==response_posts_ID_list[nn]]
        string += u'RESPONSE {0}: {1}\n'.format(unicode(nn+1),response_posts_body_list[nn])
        for comm in xrange(len(resp_comments_list)):
            string += u'RESPONSE {0} COMMENT {1}: {2}\n'.format(unicode(nn+1),unicode(comm+1),unicode(resp_comments_list[comm]))
    
    #Append end clause to string:
    string += u'END STACK EXCHANGE QUESTION: ID {}'.format(post_ID)


    #Get rid of a few most common html tags to prevent reader from getting annoying when reading:

    #Replace <a href=...>...</a> with "SOME HTML LINK"
    pattern = r'<a href="(.*)</a>'
    replace_with = "SOME HTML LINK"
    string = re.sub(pattern,replace_with,string,re.DOTALL)
    
    #Replace image links with "SOME IMAGE"
    pattern = r'<img src="(.*)alt="(.*)>'
    replace_with = "SOME IMAGE"
    string = re.sub(pattern,replace_with,string,re.DOTALL)
    
    #Remove some common xml tags that are annoying for the reader to repeat:
    pattern_list = ['p','b','li','ol','ul','sup','em']
    replace_with = ''
    for pattern in pattern_list:
        pattern_to_replace = '<{}>'.format(pattern)
        string = re.sub(pattern_to_replace,replace_with,string)
        pattern_to_replace = '</{}>'.format(pattern)
        string = re.sub(pattern_to_replace,replace_with,string)
    
    
    #Save the string in txt file:
    save_path = os.path.join(transcript_dir,'Post_{}.txt'.format(post_ID))
    with open(save_path, "w") as output:
        output.write(string.encode(utf_encode))
