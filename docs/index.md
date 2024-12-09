---
layout: page
title: Nice name! Where does it come from?
cover-img: 'assets/img/w1z5c.jpeg'
---

<link rel="stylesheet" href="assets/css/style.css">

<style>
    /*Custom css for the page*/
    .page-heading h1{
        background-color: rgba(190, 4, 4, 1);
    }
</style>

# From the *Big Screen* to your everyday life
Movies and TV shows have always been a major influence in our daily, shaping our preceptions, preferences and even cultural norms. From political messages delivered through the narrative to the emergence of new slang expressions, the impact of this medium is powerful and often underrated. Over the years, actors and the characters they played have redefined societal behaviours, starting fashion trends and even ideologies. 

For example, the famous sitcom *Friends* created "The Rachel" phenomenon. In this show, the character played by Jenifer Aniston wore an original haircut that became one of the most requested styles at hair salons across the world. It symbolized a moment where people were identifying as Rachel, were marked by the show and wanted to be just like her. Which is just what we are looking for: media influence !

{% include rachel.html %}

The case illustrates how a single person's appearance captivated the audience and shaped the tastes of thousands of people, displaying how far the power of storytelling and character design reaches. That effect is what intrigued us for our project and guided us toward its subject.
In this article, we will see how the character names in movies induce trends in baby names, particularly the years immediately following the movie release. 

# Try it yourself !
Before diving in deeper, let's give you a taste of our results. Enter any name, and see what movie potentially impacted its popularity.
{% include names_prediction.html %}

# Our *datasets* :
## The film corpus
First and most important, movies are what inspire people. They tell stories and affect our culture and lifestyle. For example, had you heard of macaws before [Rio](https://en.wikipedia.org/wiki/Rio_(2011_film)) ?

Our dataset contains movies released up to 2014 and informations such as their **unique ID**, **release date**, **genre** and the list of **characters** featured in the work.

In addition to that, we augmented it with [IMDB](https://www.imdb.com) **average rating** and **number of voters** coming from the [IMDB data files](https://datasets.imdbws.com).
We pretreated this dataset to only keep one weighted mean of votes per movie and the number of voters. We created an information 

### What makes a movie popular ?
Blockbuster movies are far more likely to influence baby name trends than obscure short films from the 1940s. To focus on culturally impactful films, we filtered out less popular ones. This was done by evaluating a movie's popularity using its average IMDb rating and the number of votes it received.
{% include rating-votes.html %}
### Genre representation
{% include top_10_genres.html %}
**NB:** A movie can belong to multiple genres.
### Important characters
Some characters retain the attention of spectators whereas others will be forgotten after a day. To account for this disparity and for simplicity, we decided to keep only the most important characters in every movie in the dataset. 

In order to measure character importance, we count the number of citation of their name in the summary of the movie and keep the most mentioned ones.

**A VENIR : exemple avec les 2-3 persos d'un film connu, fourni par Coco**


## The baby names collection
Even if it remains a simple word, your name is what you are referred as for your entire life. It represents your whole identity and often mirrors cultural trends, family traditions or historical events. A cultural event can even create a new name, as for [Anakin](https://en.wikipedia.org/wiki/Anakin_(given_name)) or [Neo](https://en.wikipedia.org/wiki/Neo_(The_Matrix)). 

We used a dataset consisting of baby names each year for the United States, United Kingdom, France and Norway to acccount for name trends.
### Most given names in the dataset
<img src="assets/img/wordcloud.png" alt="Word Cloud">

# Processes
Now that we have all this data, the next step is leveraging it to create insights into the influence of movies on baby names. How can we analyze and interpret this information to better understand this cultural impact of cinema ?
## The naïve approach
At first, we developped a naïve model that compared the popularity of a name five years before and after a movie's release. By dividing the average number of times the name is given per year before and after the movie, we get a trend metric that assesses the film's impact. 


<img src="assets/img/trend_formula.png">


Unfortunately, this is not so simple. This model doesn't account for the inverse effect, i.e. the name trend influencing the filmmakers for the name of their characters. 

To illustrate this, let's take the example of [Michael from Peter Pan](https://disney.fandom.com/wiki/Michael_Darling). According to our model, the 1953 film Peter Pan had a great impact on people naming their child Michael. Let's look at the trend graph : 


<img src="assets/img/Michael_name_trend.png">


It is clear that the film was released during a peak of popularity for the name Michael, and therefore most likely didn't play a role in its usage.





# Test 2 colonnes de texte
<div class="two-col">
  <div>
    <p>Text a gauche lorem fidsfjiji j idfisi ii ii ifii ii fi i ifjwionfnenfo nn nef iewi omeiofm owmefiom io</p>
  </div>
  <div>
    <p>Paragraph on the right for additional content or details.</p>
  </div>
</div>


# Bibliography
1. [Wikipedia: The Rachel](https://en.wikipedia.org/wiki/The_Rachel)
2. [Rachel's Picture](https://tierneysalons.com/wp-content/uploads/2023/12/0e461a848663146e13e5444687934cb0.jpg)
3. [Article on "The Rachel" by InStyle](https://www.instyle.com/the-rachel-haircut-8575551)
4. [Header Background Picture](https://imgur.com/photo-103bn-photo-116-hollywood-stars-including-leonardo-di-caprio-steven-spielberg-tom-cruise-robert-downey-jr-jack-nicholson-sean-penn-brad-pitt-martin-scorsese-dustin-hoffman-meryl-streep-jj-abrams-barbra-streisand-more-pose-toge-w1z5c) 


