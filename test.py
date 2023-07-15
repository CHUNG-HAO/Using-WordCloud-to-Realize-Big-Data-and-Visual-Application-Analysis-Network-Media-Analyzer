import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import jieba
from GoogleNews import GoogleNews
from bs4 import BeautifulSoup
import requests
import numpy as np
from PIL import ImageTk, Image
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator
from scipy.ndimage import gaussian_gradient_magnitude
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def generate_wordcloud():
    keyword = keyword_entry.get()
    output_path = output_entry.get()
    
    if not keyword:
        messagebox.showwarning("警告", "請輸入關鍵字！")
        return
    
    if not output_path:
        messagebox.showwarning("警告", "請指定文字雲生成的位置！")
        return
    
    googlenews = GoogleNews()
    googlenews.setlang('cn')
    googlenews.setperiod('d')
    googlenews.setencode('utf-8')
    googlenews.clear()
    
    googlenews.search(keyword)
    alldata = googlenews.result()
    result = googlenews.gettext()
    links = googlenews.get_links()
    
    if not result:
        messagebox.showwarning("警告", "找不到相關的新聞！")
        return
    
    df = pd.DataFrame({
        '標題': result,
        '連結': links
    })
    
    url = df['連結'][0]
    
    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
    }
    
    r = requests.get(url, headers=user_agent)
    r.encoding = "utf-8"
    web_content = r.text
    soup = BeautifulSoup(web_content, 'html.parser')
    
    articleContent = soup.find_all('p')
    
    article = []
    for p in articleContent:
        article.append(p.text)
    
    articleAll = '\n'.join(article)
    
    jieba.load_userdict('/Users/zhonghonghao/googlenews-wordCloud/dict.txt.big.txt')
    
    d = articleAll.replace('!', '').replace('／', "").replace('《', '').replace('》', '').replace('，', '').replace('。', '').replace(
        '「', '').replace('」', '').replace('（', '').replace('）', '').replace('！', '').replace('？', '').replace('、', '').replace(
        '▲', '').replace('…', '').replace('：', '')
    
    jieba.setLogLevel(10)
    
    Sentence = jieba.cut_for_search(d)
    
    with open('/Users/zhonghonghao/googlenews-wordCloud/stopword.txt', 'r', encoding="utf-8") as f:
        stopwords = f.read().split('\n')
    
    terms = {}
    for sentence in Sentence:
        if sentence in stopwords:
            continue
    
        if sentence in terms:
            terms[sentence] += 1
        else:
            terms[sentence] = 1
    
    artDf = pd.DataFrame.from_dict(terms, orient='index', columns=['詞頻'])
    artDf.sort_values(by=['詞頻'], ascending=False)
    
    img = "color-0"
    img_path = "/Users/zhonghonghao/googlenews-wordCloud/%s.png" % img
    
    mask_color = np.array(Image.open(img_path))
    mask_color = mask_color[::3, ::3]
    mask_image = mask_color.copy()
    mask_image[mask_image.sum(axis=2) == 0] = 255
    
    edges = np.mean([gaussian_gradient_magnitude(mask_color[:, :, i] / 255., 2) for i in range(3)], axis=0)
    mask_image[edges > .08] = 255
    #文字雲輸出大小跟空間以及字體n
    wc = WordCloud(font_path="/Users/zhonghonghao/googlenews-wordCloud/Kalam-Bold.ttf",
                   mask=mask_color,
                   max_font_size=35,
                   max_words=4000,
                   stopwords=stopwords,
                   margin=0,
                   relative_scaling=0,
                   )
    
    wc.generate(articleAll)
    image_colors = ImageColorGenerator(mask_color)
    wc.recolor(color_func=image_colors)
    
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(output_path)
    plt.close()
    
    # 生成圖片
    image = Image.open(output_path)
    image = image.resize((400, 400), Image.ANTIALIAS)
    image_tk = ImageTk.PhotoImage(image)
    wordcloud_label.configure(image=image_tk)
    wordcloud_label.image = image_tk

def browse_output_path():
    output_path = filedialog.asksaveasfilename(defaultextension=".png")
    if output_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, output_path)

window = tk.Tk()
window.title("新聞解析器")

# 提示標籤
keyword_prompt_label = tk.Label(window, text="請輸入新聞關鍵字：")
keyword_prompt_label.pack()

# 關鍵字標籤
keyword_entry = tk.Entry(window)
keyword_entry.pack()

# 提示標籤
output_prompt_label = tk.Label(window, text="請輸入文字雲生成的位置：")
output_prompt_label.pack()
#輸出入文字匡
output_entry = tk.Entry(window)
output_entry.pack()

# 瀏覽
browse_button = tk.Button(window, text="瀏覽", command=browse_output_path)
browse_button.pack()

# 按鈕
generate_button = tk.Button(window, text="生成文字雲", command=generate_wordcloud)
generate_button.pack()

#文字雲label
wordcloud_label = tk.Label(window)
wordcloud_label.pack()

window.mainloop()
