FROM python:3.11

COPY test.py /test.py

CMD python test.py

RUN pip install pandas
RUN pip install GoogleNews
RUN pip install numpy
RUN pip install matplotlib
RUN pip install BeautifulSoup4
RUN pip install requests
RUN pip install jieba
RUN pip install wordcloud
RUN pip install scipy



