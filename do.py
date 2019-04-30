import os
import shutil
import sqlite3
from tqdm import tqdm
import csv

def find_name_from_csv(phone):
    def get_list_of_phones(string):
        s = string.split(' ::: ')
        for i in enumerate(s):
            st = i[1]
            st = st.replace('-', '')
            st = st.replace(' ', '')        
            s[i[0]] = st[-10:]
        return s

    with open("contacts.csv", mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                for i in range(1, 6):
                    list_of_phones = get_list_of_phones(row[f'Phone {i} - Value'])
                    if phone in list_of_phones:
                        return row['Given Name']
                line_count += 1

conn = sqlite3.connect('msgstore.db')
path_to_media = "Media/"

cursor = conn.execute('''
select raw_string
from jid
where server = "s.whatsapp.net"
''')

people = []

for row in cursor:
    people.append(row[0])

population = len(people)

# people = people[0:50] # remove this


for person in tqdm(enumerate(people), total=len(people)):
    #image
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

    images = []
    for row in cursor:
        try:
            images.append(row[2].decode('ascii'))
        except:
            pass
    
    #video
    cursor = conn.execute('''
    select
        _id,
        media_mime_type,
        substr(
            substr(thumb_image,instr(thumb_image,'VID'),60)
            ,instr(substr(thumb_image,instr(thumb_image,'VID'),23),'VID')
            ,23)
    from `messages`
    where
        `key_remote_jid` like '%{}%'
        and `media_mime_type` like '%video%';
    '''.format(person[1]))
    
    videos = []
    for row in cursor:
        try:
            videos.append(row[2].decode('ascii'))
        except:
            pass

    if len(images) + len(videos)> 0:
        try:
            name = find_name_from_csv(person[1].replace('@s.whatsapp.net', '').split('91')[1])
        except:
            pass
        if name is None:
            name = person[1].strip('@s.whatsapp.net')
        try:  
            os.mkdir(os.path.join(path_to_media, "sorted", name))
        except OSError as e:  
            # print ("Creation of the directory failed \n {}".format(e.strerror))
            pass

        for image in images:
            path_to_file = os.path.join(path_to_media, "WhatsApp Images", image)
            # print("Debug: path is {}".format(path_to_image))

            try:
                is_file = os.path.isfile(path_to_file)
                if is_file:
                    try:
                        shutil.copyfile(path_to_file, os.path.join(path_to_media, "sorted", name, image))
                        # print("{} copied in {}".format(image, person[1]))
                    except:  
                        print ("Copy failed for {}".format(image))
            except:
                print("couldn't find file")


        for video in videos:
            path_to_file = os.path.join(path_to_media, "WhatsApp Video", video)
            # print("Debug: path is {}".format(path_to_image))

            try:
                is_file = os.path.isfile(path_to_file)
                if is_file:
                    try:
                        shutil.copyfile(path_to_file, os.path.join(path_to_media, "sorted", name, video))
                        # print("{} copied in {}".format(video, person[1]))
                    except:  
                        print ("Copy failed for {}".format(video))
            except:
                print("couldn't find file")        
            

conn.close()
