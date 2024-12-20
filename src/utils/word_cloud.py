from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generate_word_cloud(names_df):
    # aggregate all occurences of each name
    names_df = names_df.groupby('Name').size().reset_index(name='counts')
    # Generate a word cloud image
    wordcloud = WordCloud(width = 800, height = 400, random_state=21, max_font_size=110, background_color='white').generate(' '.join(names_df['Name']))
    # Display the generated image:
    plt.figure(figsize=(10, 7))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.show()
