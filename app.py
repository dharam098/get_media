import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import requests
import streamlit as st



# from py1337x import py1337x
# import pyratebay
# torrents = py1337x(proxy='1337x.to', cache='py1337xCache', cacheTime=500)
# import libtorrent as lt
from requests.adapters import HTTPAdapter, Retry
# from bs4 import BeautifulSoup

############TPB########################

categories = {
	'audio': {
		'code':100,
		'subs':{
			'music':1,
			'audio books':2,
			'sound clips':3,
			'flac':4,
			'other':99
		}
	},
	'video': {
		'code':200,
		'subs':{
			'movies':1,
			'movies DVDR':2,
			'music videos':3,
			'movies clips':4,
			'tv shows':5,
			'handheld':6,
			'hd movies':7,
			'hd tv shows':8,
			'3d':9,
			'other':99
		}
	},
	'applications':{
		'code':300,
		'subs':{
			'windows':1,
			'mac':2,
			'unix':3,
			'handheld':4,
			'ios':5,
			'android':6,
			'other os':99
		}
	},
	'games':{
		'code':400,
		'subs':{
			'pc':1,
			'mac':2,
			'psx':3,
			'xbox360':4,
			'wii':5,
			'handheld':6,
			'ios':7,
			'android':8,
			'other':99
		}
	},
	'porn':{
		'code':500,
		'subs':{
			'movies':1,
			'movies dvdr':2,
			'pictures':3,
			'games':4,
			'hd movies':5,
			'movie clips':6,
			'other':99
		}
	},
	'other':{
		'code':600,
		'subs':{
			'ebooks':1,
			'comics':2,
			'pictures':3,
			'covers':4,
			'physibles':5,
			'other':99
		}
	}
}


URL = "https://apibay.org/"

class Torrent:

	def __init__(self, id, name, info_hash, le, se, num_files, size, username, added, status, category):
		self.id = id
		self.url = 'https://thepiratebay.org/description.php?id='+id
		self.name = name
		self.info_hash = info_hash
		self.leechers = int(le)
		self.seeders = int(se)
		self.num_files = num_files
		self.size = size
		self.username = username
		self.added = added
		self.status = status
		self.category = category
		self.description = None

	def get_description(self):
		if self.description == None:
			r = requests.get(URL+'t.php', params={'id':self.id})
			try:
				tor = r.json()
				self.description = tor['descr']
			except Exception as e:
				st.write('Error: ', e)

	def magnet(self):
		return f'magnet:?xt=urn:btih:{self.info_hash}&dn={self.name}'

	def __str__(self):
		return f'Name: {self.name}\nHash: {self.info_hash}\nURL: {self.url}'







class tpb:
	def search(keyword, cats=[]):
		params = {
			'q':keyword,
			'cat':[]
		}
		for cat in cats:
			if cat in categories:
				params['cat'].append(str(categories[cat]['code']))
		params['cat'] = ','.join(params['cat'])

		r = requests.get(URL+'q.php', params=params)

		torrents = []
		try:
			for tor in r.json():
				torrent = Torrent(tor['id'], tor['name'], tor['info_hash'], tor['leechers'], tor['seeders'],
						tor['num_files'], tor['size'], tor['username'], tor['added'], tor['status'], tor['category'])
				torrents.append(torrent)
		except Exception as e:
			st.write('Error: ', e)
			return None

		return torrents

	def get_torrent(torrent_id):
		r = requests.get(URL+'t.php', params={'id':torrent_id})

		try:
			tor = r.json()
		except Exception as e:
			st.write('Error: ', e)
			return None

		torrent = Torrent(str(tor['id']), tor['name'], tor['info_hash'], tor['leechers'], tor['seeders'],
				tor['num_files'], tor['size'], tor['username'], tor['added'], tor['status'], tor['category'])
		torrent.description = tor['descr']
		return torrent

	def recent():
		r = requests.get(URL+'precompiled/data_top100_recent.json')
		torrents = []
		try:
			for tor in r.json():
				torrent = Torrent(tor['id'], tor['name'], tor['info_hash'], tor['leechers'], tor['seeders'],
						tor['num_files'], tor['size'], tor['username'], tor['added'], tor['status'], tor['category'])
				torrents.append(torrent)
		except Exception as e:
			st.write('Error: ', e)
			return None

		return torrents

	def top100(category=None, subc=None):
		if category is None:
			r = requests.get('https://apibay.org/precompiled/data_top100_all.json')
		else:
			if category not in categories:
				raise Exception(f"{category} is not a valid category!")
			cat_n = categories[category]['code']
			if subc is not None and subc not in categories[category]['subs']:
				raise Exception(f"{subc} is not a valid sub-category!")
			elif subc is not None:
				cat_n += categories[category]['subs'][subc]
			r = requests.get(URL+f'precompiled/data_top100_{cat_n}.json')
		torrents = []
		try:
			for tor in r.json():
				torrent = Torrent(str(tor['id']), tor['name'], tor['info_hash'], tor['leechers'], tor['seeders'],
						tor['num_files'], tor['size'], tor['username'], tor['added'], tor['status'], tor['category'])
				torrents.append(torrent)
		except Exception as e:
			st.write('Error: ', e)
			return None
		return torrents





#############TPB####################


#------FROM TMDB -------------

api_key = 'bbaa8919f1f6d5274a6835d71e37d20b'


def search_query(query):
    global api_key
    url = "https://api.themoviedb.org/3/search/movie"
    
    params = {
        'api_key' : api_key,
        'query' : query,
        'include_adult': 'true'
    }
    response = requests.get(url, params = params)
    try:
        result = response.json()

        df_result = pd.DataFrame(result['results'])
        df_result  = df_result.sort_values(by='popularity', ascending = False).reset_index(drop=True)
        df_result['poster_path'] = df_result['poster_path'].apply(lambda x: f"https://image.tmdb.org/t/p/w500{x}" if x else 'No poster available')
        df_result['release_date'] = pd.to_datetime(df_result['release_date']).dt.strftime('%d-%m-%Y')
        
        return df_result
    except:
        st.write('No Result!')
        
        return pd.DataFrame()
    



#------------GET DOWNLOAD LINKS-------------
s = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
s.mount('http://', HTTPAdapter(max_retries=retries))



api='257Z637RY5VU2XLAEWM2ICYXQHS6YG4C3I7PIGW6W6C7TMXSBBMQ'



df_torrents = pd.DataFrame({})
df_cached = pd.DataFrame({})
df_cloud = pd.DataFrame({})
df_files = pd.DataFrame({})
download_links = []
links = []
query = ''



def file_list(dic):
    if isinstance(dic, dict):
        files_in_source = (
            pd.DataFrame([item for sublist in [list(d.items()) for d in dic['rd']] for item in sublist], columns=['sno', 'dic'])
            .drop_duplicates(subset='sno', keep='first')
            .reset_index(drop=True)

        )
        df = pd.concat([files_in_source.apply(lambda row: row.dic['filename'], axis = 1)
                        ,files_in_source.apply(lambda row: row.dic['filesize'], axis = 1)], axis=1)
        return df.to_numpy()
    else:
        return []
    


def size(n):
    n=n/1000000000
    gb= "{:.2f}".format(n)
    mb= "{:.2f}".format(n*1000)
    if(n>=1):
        return f"{gb}GB"
    else:
        return f"{mb}MB"
    

#https://technoxyz.com/tamilrockers-proxy/
#https://www.1tamilmv.cafe/
# def search_1337x(query, type_ ='All'):
#     global df_torrents
#     # get torrent list by search
#     try:
#         if(type_=='All'):
#             results_dic = torrents.search(query)
#         else:
#             results_dic = torrents.search(query, category=type_)

#         df = pd.DataFrame(results_dic['items'])
#     except:
#         st.write('site not accessible')
#         return None


#     # add info hash columns
#     try:
#         df['infoHash'] = 'NA'
#         df['magnet'] = 'NA'
#         for row in df.itertuples():
#             try:
#                 torrent_info = torrents.info(link=row.link)
#                 df['infoHash'].iloc[row.Index] = torrent_info['infoHash']
#                 df['magnet'].iloc[row.Index] = torrent_info['magnetLink']
#             except:
#                 pass
#         df = df[df['infoHash'] != 'NA']

#     except:
#         st.write('info hash not added')
#         return df[['name', 'seeders', 'leechers', 'size', 'time', 'uploader']]
#     df_torrents = df[['name', 'seeders', 'leechers', 'size', 'time', 'uploader', 'infoHash', 'magnet']]

#     return df_torrents[['name', 'seeders', 'leechers', 'size', 'time', 'uploader']]




def search_tpb(query):
    global df_torrents
    torrents = tpb.search(query, ['video'])
    list_search_results=[]
    for torrent in torrents:
        list_search_results.append({'name':torrent.name, 'seeders': torrent.seeders, 'leechers': torrent.leechers, 'size':torrent.size, 'time': torrent.added, 'num_files': torrent.num_files, 'infoHash': torrent.info_hash, 'magnet': torrent.magnet()})

    df_torrents = pd.DataFrame(list_search_results)
    df_torrents['time'] = pd.to_numeric(df_torrents['time'], errors='coerce')
    df_torrents['time'] = pd.to_datetime(df_torrents['time'],unit='s')
    df_torrents['size']=df_torrents['size'].astype('int64').apply(size)

    return df_torrents[['name', 'seeders', 'leechers','size', 'time', 'num_files']]






def search_anime_tosho(title):
    global df_torrents
    title = title.replace(" ","+")
    url = f"https://animetosho.org/search?q={title}"
    page = s.get(url)

    #filter sources
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="content")
    results_links = results.find_all("div", class_="home_list_entry")

    # make datafrmae of sources
    l=[]
    for results_link in results_links:
        title = results_link.find("div", class_="link").text
        magnet_url = results_link.find("a", href=True, string='Magnet')['href']
        info_hash = str(lt.parse_magnet_uri(magnet_url).info_hash)
        size = results_link.find("div", class_="size").text
        date = results_link.find("div", class_="date")['title'][20:]
        try:
            num_files = results_link.find("em").text.split(' ')[0][1:]
        except:
            num_files = '1'
        l.append((title, size, date, num_files, magnet_url, info_hash))

    df=pd.DataFrame(l)
    df.columns = ['name', 'size', 'time', 'number_of_files', 'magnet', 'infoHash']

    #refine source df
    df=(
        df
        .drop_duplicates(subset='infoHash', keep="first")
        .reset_index(drop=True)
    )
    df_torrents = df
    return df




def filter_cached():
        global df_cached
        df = df_torrents.copy()
        #check cached
        hash_list = '/'.join(df.loc[:,'infoHash'].to_list())
        url = f"https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{hash_list}"
        response = requests.get(
            url
            ,headers={"Authorization": f"Bearer {api}"}
        )
        df['cache_info'] = df.apply(lambda row: file_list(response.json()[row.infoHash.lower()]), axis = 1)
        df['number_of_files'] = df.apply(lambda row: len(row.cache_info), axis = 1)
        df=df[df['number_of_files']>0].reset_index(drop=True)
        df_cached=df

        return df_cached[['name', 'size', 'time', 'number_of_files']]



def get_debrid_link(i):
    global df_cloud, df_files, links
    # check link in cloud
    try:
        st.write('Cloud scanning')
        response = requests.get(
            'https://api.real-debrid.com/rest/1.0/torrents'
            ,headers={"Authorization": f"Bearer {api}"}
        )
        df_cloud = pd.DataFrame(response.json())
        info_hash = df_cached.loc[i, 'infoHash'].lower()
        matching_indexes = df_cloud.index[df_cloud['hash'] == info_hash].to_list()
        if len(matching_indexes):
            
            id_ = df_cloud.loc[matching_indexes[0], 'id']
            url = f"https://api.real-debrid.com/rest/1.0/torrents/info/{id_}"
            response = requests.get(
                url
                ,headers={"Authorization": f"Bearer {api}"}
            )
            links = response.json()['links']
            df_files = pd.DataFrame(response.json()['files']).drop(['id', 'selected'], axis =1).rename({'path':'filename'}, axis=1)
            df_files['size']=df_files['bytes'].apply(size)
            df_files.drop(['bytes'], axis=1, inplace=True)
            st.write('Found!')
            return df_files
        else:
            st.write('Pass')
    except:
        st.write('cloud checking failed')
        pass



    #add magnet to debrid
    try:
        magnet = df_cached.loc[i,'magnet']

        response = requests.post(
            'https://api.real-debrid.com/rest/1.0/torrents/addMagnet'
            ,{"magnet" : magnet}
            ,headers={"Authorization": f"Bearer {api}"}
        )
        if not response.ok:
            st.write("error adding magnet")
            return None
    except:
        st.write('error adding magnet')
        return None

    #start magnet link
    try:
        id_ = response.json()['id']
        url = f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{id_}"
        response = requests.post(
            url
            ,{"files": "all"}
            ,headers={"Authorization": f"Bearer {api}"}
        )

        if not response.ok:
            st.write("error starting magnet")
            return None

    except:
        st.write('error starting magnet')
        return None


    #get cached magnet link
    try:
        url = f"https://api.real-debrid.com/rest/1.0/torrents/info/{id_}"
        response = requests.get(
            url
            ,headers={"Authorization": f"Bearer {api}"}
        )
        links = response.json()['links']
        if response.ok:
            st.write('magnet added')
        else:
            st.write('error getting files')
            return None
    except:
        st.write('error getting files')
        return None

    df_files= pd.DataFrame(response.json()['files']).drop(['id', 'selected'], axis =1).rename({'path':'filename'}, axis=1)
    df_files['size']=df_files['bytes'].apply(size)
    df_files.drop(['bytes'], axis=1, inplace=True)
    return df_files




def unrestrict(i=[-1]):
    global download_links
    if isinstance(i, int):
        i_=[]
        i_.append(i)
        i=i_

    result = []
    download_links = []

    #get unrestricted link
    for j,link in enumerate(links):
        if j not in i and i!=[-1]:
            continue
        try:
            response = requests.post(
                'https://api.real-debrid.com/rest/1.0/unrestrict/link'
                ,{"link": link}
                ,headers={"Authorization": f"Bearer {api}"}
            )


            if not response.ok:
                st.write('error unrestricting')
                return None

            response = response.json()
            result.append((response['filename'],response['download']))
            download_links.append(response['download'])



        except:
            st.write('error unrestricting')
            return None
    download_links = result
    return result



def write_with_color(text, color):
    st.markdown(f"<p style='color:{color}'>{text}</p>", unsafe_allow_html=True)

def write_with_larger_font(text, font_size):
    st.markdown(f"<p style='font-size:{font_size}px'>{text}</p>", unsafe_allow_html=True)


def set_text_style(text, background_color, text_color):
    styled_text = f"<p style='background-color: {background_color}; color: {text_color};'>{text}</p>"
    st.markdown(styled_text, unsafe_allow_html=True)


def show_scrape_results(title):
    search_tpb(title)
    # search_1337x(title)
    filter_cached()
    st.session_state['df_cached'] = df_cached
    dict = st.session_state['df_selected_tmdb_result']
    number_of_results = len(df_cached)
    st.write('---')
    image_column, text_column  = st.columns((1,5))

    with image_column:
        st.image(Image.open(BytesIO(requests.get(dict['poster_path']).content)))

    with text_column:
        st.subheader(title)
        st.write(dict['overview'])
        date, button = st.columns((1,7))
        with date:
            st.write(dict['release_date'])
    


    for i in range(0, number_of_results):
        # st.write('---') 
        name, size, time, number_of_files, click = st.columns((8,1,2,1,1))
        with name:
            # write_with_larger_font(df_cached.iloc[i].loc['name'], 20)
            write_with_color(df_cached.iloc[i].loc['name'], 'LavenderBlush')
        with size:
            st.write(df_cached.iloc[i].loc['size'])
        with time:
            st.write(str(df_cached.iloc[i].loc['time']))
        with number_of_files:
            st.write(str(df_cached.iloc[i].loc['number_of_files']))
        with click:
            buttons_for_scrape_results.append(st.button('*', key = f"s{i}"))
    

##############################################################    
        
width = 200
height = 300
flag=0
title = ''
black_image = Image.new("RGB", (width, height), color="black")
df_tmdb_results = pd.DataFrame()
buttons =[]
buttons_for_scrape_results = []   
            

st.set_page_config(page_title="My Webpage", layout="wide")

if 'click_' not in st.session_state:
    st.session_state['click_'] = False

if 'submit_clicked' not in st.session_state:
    st.session_state['submit_clicked'] = False

if 'title' not in st.session_state:
    st.session_state['title'] = ' '

if 'df_selected_tmdb_result' not in st.session_state:
    st.session_state['df_selected_tmdb_result'] = {}

if 'scrape_button_click' not in st.session_state:
    st.session_state['scrape_button_click'] = False

if 'selected_scrape_result' not in st.session_state:
    st.session_state['selected_scrape_result'] = -1

if 'df_cached' not in st.session_state:
    st.session_state['df_cached'] = pd.DataFrame()



query = st.text_input('Search..')
button_clicked = st.button('Submit')


if button_clicked:
    st.session_state['submit_clicked'] = True

if st.session_state['submit_clicked']:
    st.session_state['click_'] = False
    
    df_tmdb_results = search_query(query)
    no_of_results = len(df_tmdb_results)
    st.write(f"{no_of_results} Results")
    st.header(query)
    st.write('##')
    placeholder = []
    

    for i in range(0, no_of_results):
        title = df_tmdb_results.iloc[i].loc['title']
        st.write('---')
        placeholder.append(st.empty())
        with placeholder[-1]:

            image_column, text_column  = st.columns((1,5))

            with image_column:
                st.image(black_image)


            with text_column:
                st.subheader(title)
                st.write(df_tmdb_results.iloc[i].loc['overview'])
                date, button = st.columns((1,7))
                with date:
                    st.write(df_tmdb_results.iloc[i].loc['release_date'])
                with button: 
                    button_ = st.button('scrape', key = f"button{i}")

                    buttons.append(button_) 
                    if button_:
                        st.session_state['click_'] = True
                        break

                        
                    

    if not st.session_state['click_']:
        for j in range(0, no_of_results):
            try:

                with placeholder[j]:
                    image_column, text_column  = st.columns((1,5))
                    with image_column:
                        st.image(Image.open(BytesIO(requests.get(df_tmdb_results.iloc[j].loc['poster_path']).content)))
            except:
                pass

    
    if sum(buttons):
        st.session_state['click_'] = True
        i = [index for index, value in enumerate(buttons) if value][0]
        st.session_state['title'] = df_tmdb_results.iloc[i].loc['title']
        st.session_state['df_selected_tmdb_result'] = df_tmdb_results.iloc[i].to_dict()
        st.session_state['submit_clicked'] = False
        st.experimental_rerun()

if st.session_state.get('click_', False):
    show_scrape_results(st.session_state['title'])
    if sum(buttons_for_scrape_results):
        st.session_state['scrape_button_click'] = True
        st.session_state['selected_scrape_result'] = [index for index, value in enumerate(buttons_for_scrape_results) if value][0]        
        st.session_state['click_']= False
        st.experimental_rerun()

    

if st.session_state.get('scrape_button_click', False):
    df_cached = st.session_state['df_cached']
    get_debrid_link(st.session_state['selected_scrape_result'])
    debrid_result = unrestrict()
    for file in debrid_result:
        name1 = file[0]
        link = file[1]
        link = f"[{name1}]({link})"
        st.markdown(link, unsafe_allow_html=True)
    st.session_state['scrape_button_click'] = False
        
        










