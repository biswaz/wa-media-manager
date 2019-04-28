import sqlite3
import os
import shutil

conn = sqlite3.connect('msgstore.db')
path_to_media = "wa_img/"

cursor = conn.execute('''
select raw_string
from jid
where server = "s.whatsapp.net"
''')

people = []

for row in cursor:
    people.append(row[0])

population = len(people)

for person in enumerate(people):
    cursor = conn.execute('''
    select

        _id,
        media_mime_type,
        substr(
            substr(thumb_image,instr(thumb_image,'IMG'),60)
            ,instr(substr(thumb_image,instr(thumb_image,'IMG'),23),'IMG')
            ,23)
    from `messages`
    where
        `key_remote_jid` like '%{}%'
        and `media_mime_type` like '%image%';
    '''.format(person[1]))

    media = []
    for row in cursor:
        try:
            media.append(row[2].decode('ascii'))
        except:
            pass

    try:  
        os.mkdir(os.path.join(path_to_media, person[1]))
    except OSError:  
        print ("Creation of the directory failed")

    for file in media:
        path_to_file = os.path.join(path_to_media, file)
        print("Debug: path is {}".format(path_to_file))

        try:
            does_file_exist = os.path.isfile(path_to_file)
        except:
            pass
        if does_file_exist:
            try:
                shutil.copyfile(path_to_file, os.path.join(path_to_media, person[1], file))
            except:  
                print ("Copy failed for {}".format(file))
    print("{} of {} complete".format(person[0], population))

conn.close()