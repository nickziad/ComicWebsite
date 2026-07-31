import pathlib
from zipfile import ZipFile
from db import query, execute, update
from werkzeug.utils import secure_filename
import os
from concurrent.futures import ThreadPoolExecutor


'''
Sheesh, this is the big models.py. The heart of everything catalogue, I would say. 
It has a bunch of functions that are vital to make the catalogue service work. 
It also has concurrency! The concurrency part had to be added, because we need to convert the .cbz files to a bunch of pages so they can be read. 
Contrary to the monolithic build, everything is in here. Before some stuff was in another place just to have a bit more OOP and a nicer look.
Below are the global variables that can be adjusted. If ITEM_FOLDER ever needs to change, there's no need to go looking for it everywhere, since it's right here!
'''
ALLOWED_EXTENSIONS_COVER = {'jpg','png',}
ALLOWED_EXTENSIONS_ISSUE = {'cbz'}
ITEM_FOLDER = "/items"

executor = ThreadPoolExecutor(2)

'''
Both allowed do the same thing, but better to have them in different functions since 1 is for the cover page and another is for issues
'''
def allowed_cover(filename):
    return '.' in filename and \
    filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS_COVER

def allowed_issue(filename):
    return '.' in filename and \
    filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS_ISSUE

#gets all comics. publisher is an optional parameter. 
def get_comics(publisher=None):
    
    if publisher:
        comics = query("""
                    SELECT s.title, s.front_page, publisher_name, s.id
                    FROM comic_series AS s
                    INNER JOIN publishers AS p ON s.publisher_id = p.id WHERE p.publisher_name = ? """, [publisher])
    else:
        comics = query("""
                    SELECT s.title, s.front_page, publisher_name, s.id
                    FROM comic_series AS s
                    INNER JOIN publishers AS p ON s.publisher_id = p.id""")
    return comics

#God forbid somebody wants to delete their comics, but there's an option.
def delete_comic(id):

    comic = query("""
                  DELETE FROM comic_series WHERE user_id = ?""", [id])
    
    if comic > 1:
        return True

    else:
        return False

#gets specific comic
def get_comic(id):

    comic = query("""
                SELECT s.id,s.title, s.front_page,publisher_name, s.path_to_series,s.owner_id, s.issues_count
                FROM comic_series AS s
                INNER JOIN publishers AS p ON s.publisher_id = p.id 
                WHERE s.id =?""",[id,],True)
    return comic 

#gets specific issue
def get_issue(id):

    issue = query("""
                  SELECT * FROM comic_issues WHERE series_id = ?""",[id,], True)
    return issue

#gets how many issues a comic has. Used in the html to know how many issues to display
def get_comic_issue_count(id):

    issue_count = query("""
                        SELECT issues_count FROM comic_series WHERE id = ?""", [id], True)
    return issue_count['issues_count']

def get_user_added_comics(id):
    comics = query("""
    SELECT 
        s.title, s.front_page, publisher_name, s.path_to_series, s.id
            FROM comic_series AS s
            INNER JOIN publishers AS p ON s.publisher_id = p.id 
            WHERE s.owner_id =?
        """,[id])
    print(comics)
    return comics

#updates comic count. Used in insert_issue to update the comic count. The sole reason why update() in db was born
def update_comic_issue_count(id):
    updated = update("""
          UPDATE comic_series SET issues_count = issues_count + 1 WHERE id = ?""", [id])
    return updated

#inserts series and calls upload_series to get it uplaoded to ITEM_FOLDER. Return boolean and status code to know if there was success.
def insert_series(title, front_page,is_active, publisher, category, owner_id):
    
    cover = upload_series(title, front_page)
    #if success, it's added to the database.
    if cover:
        execute("""
        INSERT INTO comic_series
        (title, front_page, is_active, publisher_id,
            category_id, owner_id, path_to_series) 
        VALUES(?,?,?,?,?,?,?)""",
                        [title, cover[1],  is_active, publisher, category, owner_id, cover[0]])
        return True, 201
    else:
        return False, 404
'''
inserts issues. It acquires the path to the comic and with that it can upload the issue to the ITEM_FOLDER.
Also updates issue count and calls the executor so it can unpack the .cbz
'''
def insert_issue(series_id, file, owner_id):
    
    row = query("SELECT path_to_series FROM comic_series WHERE id = ?", [series_id], True)
    base_series_path = row["path_to_series"]  # e.g. Comics/batman

    issue_number = get_comic_issue_count(series_id) + 1

    issue = upload_issue(base_series_path, file, issue_number)
    
    execute("""
        INSERT INTO comic_issues (series_id, issue_number,file_path, owner_id)
        VALUES (?, ?, ?,?)
    """,[series_id,issue_number, issue, owner_id])

    update_comic_issue_count(series_id)
    issue = os.path.join(ITEM_FOLDER, issue)
    
    executor.submit(build_issues, issue)

    return True, 201


# ------------------------------------------------------
# ----------------Uploading to folder stuff-------------
# ------------------------------------------------------

'''
Makes sure cover_file and its extension is good to go. Then it creates a new folder and puts the cover in. returns paths
paths has the base address and the cover address. These are saved in the database when upload_series returns to insert_series.
'''
def upload_series(title, cover_file):

    if cover_file and allowed_cover(cover_file.filename):
        filename = secure_filename(title.lower().replace(" ","-"))
        
        paths = []

        base_Path = os.path.join(ITEM_FOLDER, "Comics", filename)
        os.makedirs(base_Path, exist_ok=True)

        ext = cover_file.filename.rsplit('.',1)[1]
        
        cover_path = os.path.join(base_Path,f"cover.{ext}")
        cover_file.save(cover_path)
        
        cover_rel_path = f"Comics/{filename}/cover.{ext}"
        base_rel_path =f"Comics/{filename}"
        paths.extend((base_rel_path,cover_rel_path))
        return paths
    
    return False

#Does basically the same as upload_series. Has an additional base series path parameter, which is used to create the proper folder for the issue.
def upload_issue(base_series_path, file, issue_number):

    issue_folder_name = secure_filename(str(issue_number))
    issue_path = os.path.join(ITEM_FOLDER, base_series_path, "Issues", issue_folder_name)
    os.makedirs(issue_path, exist_ok=True)

    if allowed_issue(file.filename):
        ext = file.filename.rsplit('.',1)[1]
        filename = f"issue-{issue_number}.{ext}"

        full_path = os.path.join(issue_path, filename)
        file.save(full_path)

        rel_path = f"{base_series_path}/Issues/{issue_folder_name}/{filename}"
        
        return rel_path
    
    return False

#.cbz is actually zipFile! Who knew. so it just gets the path to the .cbz and then unzips it and return empty handed. Doesn't need to do anymore
def build_issues(file_path):
    
    print(f"relative file path: {file_path}")
    file_path = os.path.abspath(file_path)

    base_path = pathlib.Path(file_path).parent

    print("[build_issues] file_path (abs):", file_path)
    print("[build_issues] extract to:", base_path)
    
    with ZipFile(file_path,"r") as zObject:
        zObject.extractall(base_path)

    return
