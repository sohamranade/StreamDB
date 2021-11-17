# Fall 2021 Introduction to DAtabases Team Project

## Team members

| Name              |   UNI         | Github username |
| :---              |    :----:     |          ---:   |
| Soham Ranade      | ssr2182       | sohamrande      |
| Adit Deshmukh     | avd2133       | adit-10         |

## PostgreSQL account

- ssr2182

## Web app URL

- 

## Parts from original proposal implemented

- Get comprehensive information about Movies, TV shows, Artists and streaming platforms
- Filter Movies using any combination of featues such as name, rating, language, genre, artists
- Best platform for user based on preferences
- Find artists who worked in a particular Movie or TV show

## Parts from original proposal not implemented

- Merging and an or filters for complex search

## New features added

- Filter TV shows using preferences
- Rank Movie results by rating or viewership 
- Users have ability to add ratings and reviews for movies and tv shows (after authentication)
- Leaderboard results show users highest rated Movies and TV shows as well as highest grossing films
- Dynamically see changes in ratings on the leaderboard when you update a rating

## Most interesting web pages

Movie/TV show filtering: The user gets to set preferences related to name, language, genre, artists and platform. The user can also sort the resuluts on the basis of rating and earning(only Movies). Any subset of these filters can be specified. Some of these need joining with additional tables. The query is dynamically created to account for all the preferences that the user has provided to get the correct result. 

Best Platform for user: Different users have different preferences when it comes to favorite movies or TV shows. We let the users specify what they love, eg a particular artist, genre or langague and lists the number of entertainment options each streaming platform provies for that particular setting, helping users decide the best streaming platform for them.
