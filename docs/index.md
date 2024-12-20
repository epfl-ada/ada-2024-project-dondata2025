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
But enough talking—now it’s your turn to explore! Ever wondered if your favorite movie left its mark on baby name trends? We used Meta's [Prophet](https://facebook.github.io/prophet/docs/quick_start.html) AI model to predict what the trend of a name would look like, and compare it to the actual trend to see if the release of a movie influenced it. Here is a selection of some cases for you to preview :

{% include results_display.html %}

# Our datasets :
To find out how movies influence baby name trends, we worked with 2 datasets. The first one is all about movies. It’s our link to the big screen and helps us track the cultural buzz created by blockbuster hits. The second dataset dives into baby names across four countries: the United States, United Kingdom, France, and Norway. It lets us see how names rise and fall in popularity over time, giving us the some insight to on what’s happening in cinemas to real-world trends. Now, let’s dive into the data !


## The film corpus
Movies are more than just entertainment, they inspire us, shape our culture, and sometimes even change the way we see the world. Think about it: would you have known about macaws if [Rio](https://en.wikipedia.org/wiki/Rio_(2011_film)) hadn’t brought them to life on screen?*
To explore these connections, our dataset includes a collection of films released up to 2014. It’s packed with details such as:
<ul>
  <li><strong>Movie IDs</strong> to uniquely identify each film.</li>
  <li><strong>Release Dates</strong> to trace when the hype began.</li>
  <li><strong>Genres</strong> to explore trends across action, comedy, drama, and more.</li>
  <li><strong>Character Names</strong> — the stars of our analysis! — to connect the dots between movies and baby name trends.</li>
</ul>

To make the dataset even more insightful, we added extra details from [IMDB](https://www.imdb.com), including **average ratings** and the **number of votes** each movie received. After some preprocessing, we ensured movie has a single weighted rating and vote count.



### What makes a movie popular ?
Blockbuster movies are far more likely to influence baby name trends than obscure short films from the 1940s. To focus on culturally impactful films, we filtered out less popular ones. This was done by evaluating a movie's popularity using its average IMDb rating and the number of votes it received.
{% include rating-votes.html %}

### Genre representation
The genre of a movie is a key indicator of themes and storytelling style of a movie. We will look at its distribution in the dataset.

{% include top_10_genres.html %}
**NB:** A movie can belong to multiple genres.

Characters in movie genres often follow archetypes, including how they are named. Here are the most common names by genre.
{% include top_10_names_by_genres.html %}
### Important characters
Some characters captivate the audience's attention, leaving a lasting impression, while others fade from memory within a day. To address this disparity and simplify our analysis, we decided to retain only the most important characters in each movie in our dataset.

To measure character importance, we counted the number of times their names appeared in the movie's summary and selected the most frequently mentioned ones. Below, we provide partial plot summaries of well-known movies such as Star Wars: Episode IV - A New Hope, Titanic, and Back to the Future. In each summary, we highlighted the characters' names as detected by our technique.

However, this method is not flawless. You may notice some undetected names (highlighted in red), particularly when they are highly fictional or unusual.

{% include plots_carrousel.html %}

## The baby names collection
Even if it remains a simple word, your name is what you are referred as for your entire life. It represents your whole identity and often mirrors cultural trends, family traditions or historical events.

We used a dataset consisting of baby names each year for the United States, United Kingdom, France and Norway to acccount for name trends.

### Most given names in the dataset

Here is a word cloud plot representing the most given names in the dataset. The bigger the name is, the more it has been given to newborns.
<div style="display: flex; justify-content: center; align-items:center; width:100%;">
  <img src="assets/img/wordcloud.png" width="80%" alt="Word Cloud">
</div>

# Processes

Now that we have all this data, the next step is leveraging it to create insights into the influence of movies on baby names. How can we analyze and interpret this information to better understand this cultural impact of cinema ?

## The naïve approach
At first, we developped a naïve model that compared the popularity of a name five years before and after a movie's release. By substracting the average number of times the name is given per year before and after the movie, we get a trend metric that assesses the film's impact. 

<script src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" type="text/javascript"></script>

$$ metric = \text{average count of a name 5 years after} \\ - \text{average count of a name 5 years before} $$ 

Unfortunately, this is not so simple. This model doesn't account for the inverse effect, i.e. the name trend influencing the filmmakers for the name of their characters. 

To illustrate this, let's take the example of [Michael from Peter Pan](https://disney.fandom.com/wiki/Michael_Darling). According to our model, the 1953 film Peter Pan had a great impact on people naming their child Michael. Let's look at the trend graph : 


{% include michael_trend.html %}


It is clear that the film was released during a peak of popularity for the name Michael, and therefore most likely didn't play a role in its usage.

This computed score is not totally useless, since it still allows us to elimate all the character names were there is no chances of influence (decrease in the mean after the movie release). When doing this computation, you can also check if a name was **invented** by the movie by checking that there is no record of the name before the release date. 

## Using Machine Learning predicitions

The metric given in the section above identifies which names are potential candidates, but we still need to fin a way to know if the name was actually influenced.

To do so, we use a technique called **Interrupted Time Series**. Basically, what we do is taking the data about a name **before a movie was released**, and trying to deduce **what would a normal evolution for the name be** with machine a learning model. 

This will leave us with two curves that represent the names evolution after the release of the movie. One containing the actual data from the datasets and one that was predicted based on the previous counts (predicted). If the **actual curve is much higher than the predicted one**, we can assume that the movie has influenced this name! 

# Results
Using this method, we can generate a list of films that have influenced the general trend for first names. Now that we produced our results, let's take a look at them. 

## Movie influence over time
One might come to the idea that cultural and cinematic impact fluctuates over time. Here are the number of names influenced by movie characters over decades from the 60s to the 00s.

{% include influenced_names_per_era.html %}

#### Several observations :
A steady growth is observed in the 60s and 70s, corresponding to the late stage of the [Golden Age of Hollywood](https://en.wikipedia.org/wiki/Classical_Hollywood_cinema#1927–1960:_Sound_era_and_the_Golden_Age_of_Hollywood). This period marks the rise of popular movies and the increase in revenue the cinema industry generates.

The 80s exhibit a significant increase, influencing over a **hundred** names. With the release of iconic movies such as [Alien](https://en.wikipedia.org/wiki/Alien_(film)), 
[E.T.](https://en.wikipedia.org/wiki/E.T._the_Extra-Terrestrial) and the first three [Indiana Jones](https://en.wikipedia.org/wiki/Indiana_Jones), this era represents the start of the Blockbuster age, giving Hollywood a worldwide reach and a foothold on Pop Culture icons.

Cinema reached its peak influence over baby names in the 90s. This apogee can be linked with the [Disney Renaissance](https://en.wikipedia.org/wiki/Disney_Renaissance) period and the emergence of globally beloved characters accross various animated and live-action films. During this era, cinema was the main medium for conveying stories and entertaining the people.

Y2K brings a noticeable decline in influenced names, dropping back to similar levels as the 70s despite having a much more developped industry. This indicates a shift in cultural trends, where people turn to the rising internet and streaming services, giving less attention to feature-length films. This period reflects the fragmentation of media influence and the appearance of new ways of telling stories.


## Birth of a new name
Some films have such a cultural impact that they leave a lasting impression on the audience with their characters and make them remember their name, even when they don't even exist or are practically unused. These events lead to the resurgence of an unpopular name or even the creation of a new one.

{% include newnames_carrousel.html %}

## Is there a movie genre that has a stronger influence on names ?
Does an adventurous film, where the hero embodies all the traits we aspire to—bravery, charisma, and triumph—leave a stronger mark than a heart-wrenching drama? Or is it the tension and excitement of a thriller that makes a name stick in our minds?

In this part, we set out to explore which movie genres resonate the most, in other words, whether certain movie genres have a stronger influence on baby names than others. 
To measure this, we used the difference-mean metric—a score that represents the gap between a name’s real trend curve after a movie’s release and its predicted curve if the movie had never existed. Simply put, the higher the score, the greater the movie’s impact on that name.
The results are clear: Action, Thriller, and Drama stand out as the most influential genres. These types of movies, often featuring intense storytelling and memorable characters, seem to leave a stronger mark on audiences. The treemap confirms this, highlighting names like Ethan and Emma that dominate multiple categories, particularly in high-stakes genres like Action and Thriller.


{% include top_10_influenced_genres.html %}



This treemap is a representation of the amplitude of the influence of movie genre:
(For this analysis, we are aware that our metric, the distance between curves, is not completely reliable, so we won't conclude anything concretely for the magnitude influence of genre movies on names.)

{% include treemap_top3_by_genre.html %}


This other treemap shows the most influent genre and the top 3 names for each of them, in term  propotion.

{% include treemap_top3_by_genre_by_count.html %}


While we might expect romantic films or period pieces to lead the charge, it’s the fast-paced, emotionally gripping genres that truly shape naming trends. It’s as if the excitement and tension of these stories spill over into real life, inspiring parents to choose names that reflect the bold and impactful characters they’ve seen on screen.
The two treemaps reveal interesting insights about the influence of movie genres on baby names. The top three genres—Action, Drama, and Thriller—consistently dominate both in amplitude (the magnitude of influence) and in occurrence (the number of names impacted). However, the patterns start to diverge beyond these top genres.

For instance, Comedy ranks 5th in influence by amplitude but climbs to 4th in occurrence. This suggests that while comedic movies impact a larger number of names, their influence on each name's trend is relatively smaller compared to genres like Action or Drama.

On the other hand, Adventure stands out for its higher influence in amplitude than in occurrence. This indicates that while fewer names are impacted by Adventure movies, the magnitude of the impact on those names is significant—suggesting strong but targeted influence.

Overall, the three most influential genres—Action, Drama, and Thriller—not only reach a broad range of names but also leave a strong mark on each name’s trend. They balance both breadth (occurrence) and depth (amplitude) in their cultural impact on naming trends.





## Do movies shape names differently for men and women ?

When the cinema brings unforgettable characters to life—be they fearless adventurers, clever strategists, or tender-hearted dreamers—how do they influence the names we pass on to the next generation? In this spotlight, we’ll explore how movies shape naming trends differently based on gender. Do male and female characters leave distinct marks on birth certificates, or does the silver screen affect all names equally? Let’s roll the film and uncover how the stories we love might shape the names we choose.

First, let's look at the repartition of gender amongst the names influenced by movies.

{% include pie_chart_gender.html %}

Interesting! For much of cinematic history, male characters have dominated the spotlight, often portrayed as heroes, leaders, and pivotal figures in stories that shape popular culture. This historical trend is reflected in our data, where approximately 3 out of 4 influenced names are male.

To better understand how movies influence names, we look at the distribution of influenced names across different movie genres. This will help us see if certain genres have a stronger impact on male or female names.

{% include plot_genre_gender_influence.html %}

The chart reveals that male names dominate the influence across almost all genres, which aligns with the broader trend where 3 out of 4 influenced names are male. This pattern holds consistent in most cases. We could have expected this outcome due to our previous observation about the historical dominance of male characters in movies. However, the Comedy genre is a surprising exception, showing an almost 50/50 split between male and female names influenced.


# Limitations of our project

<div style="display: flex; justify-content: center; align-items:center; width:100%;">
<div>
  <blockquote>
    <p>Give me the <strong>positions and velocities</strong> of all the particles in the universe, and <strong>I will predict the future.</strong></p>
  </blockquote>
  <p>—Marquis Pierre Simon de Laplace</p>
</div>
</div>
<style>

  div:has(> blockquote) {
    background-color: #ededed;
    margin: 10px auto;
    padding: 15px;
    border-radius: 5px;
    width: 80%;
    box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
  }

  blockquote p::before {
    content: '\201C';
  }

  blockquote p::after {
    content: '\201D';
  }

  blockquote + p {
    text-align: right;
  }

</style>

### Detection of character names

Our techniques, while effective, are not without limitations. The model used to detect character names may occasionally miss some or erroneously include others. For instance, in Star Wars: Episode IV - A New Hope, a "Jedi Knight" was detected multiple times, while Leia's name was entirely overlooked. Despite such issues, we can often mitigate them, as names are typically detected in other movies or not matched with legitimate names in our dataset.

These discrepancies may also arise in specific cases, such as the name "Doctor," which has over 40 matches in the U.S. dataset. This suggests that Americans might name their children "Doctor," humorously implying that they are born with a Ph.D.

### Confounders

Dealing with external events was a significant challenge for us. On multiple occasions, we were surprised by unexpected results. However, upon closer analysis, external events often explained these sudden changes. The Harry Potter saga serves as an excellent example to illustrate this point. Harry Potter and the Philosopher's Stone was published in 1997, while the movie adaptation premiered in cinemas in 2001. By the time the movie was released, the hype around Harry’s name had already begun, making it difficult for our model to accurately predict its influence.

# Bibliography
1. [Wikipedia: The Rachel](https://en.wikipedia.org/wiki/The_Rachel)
2. [Rachel's Picture](https://tierneysalons.com/wp-content/uploads/2023/12/0e461a848663146e13e5444687934cb0.jpg)
3. [Article on "The Rachel" by InStyle](https://www.instyle.com/the-rachel-haircut-8575551)
4. [Header Background Picture](https://imgur.com/photo-103bn-photo-116-hollywood-stars-including-leonardo-di-caprio-steven-spielberg-tom-cruise-robert-downey-jr-jack-nicholson-sean-penn-brad-pitt-martin-scorsese-dustin-hoffman-meryl-streep-jj-abrams-barbra-streisand-more-pose-toge-w1z5c) 


