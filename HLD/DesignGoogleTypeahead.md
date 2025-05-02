# Google TypeAhead / Search
Suggested content
## Functional Requirements
- We will show only 5 suggestions
- We will show suggestion after every char is typed or deleted
- Ranking
  - ranking will be based on frequency of searches
  - will give more weightage to keywords which are popular recently (recency factor)
    
## Non Functional Requirements
- consistency vs availability
  - we will choose availability
- consistency vs low latency
  - we will choose low latency

## Back of the envelope calculation
Assumptions
1. DAU of Google - 1B
2. Avg no of searches per person per day - 10
3. Avg no of character typed before search - 5

Total search suggestions per day - 1B * 10 *5 = 50B
Peak RPS(Request per second) 
1. 86400sec (24*60*60) ~ 10^5
2. 10B / 10^5 = 10^5 = 500k req per second
3. minimum 2 words are there in a search, so rps = 2*500k = 1M rps

Size of the data
- Brute force solution, we use a map to store keyword as key frequency as value
- Out of 10B queries per day, suppose 10% is unique, which means 1B queries per day
- Avg length of the query - 10 character = 10bits
- so, data stored per day is 10bits * 1B = 10B bits per day
- so, data stored per year is 400 day * 10B bits = 400 * 10^10 B => 400 * 10^9 B => 400 GB => 4TB
- so, data store for 5 years = 5*4 TB = 20 TB
- Therefore we need to shard the data

Read or write heavy
- Read => 50B per day
- Write => 10B per day
- Read: write ratio is 5:1
- So, the system is both read and write heavy
Ratio has to be 100:1 or 50:1 for it to be just read heavy


## APIs
1. List<Suggestions> getSuggestions(prefix)
2. void handleQuery(query)

## Deep Dive

How will I store data

Recency
- We can give more preferance to recent score.
- Use concept of time decay
- Divide the accumulated score of a keyword by 10 after each day.
- This will reduce the weightage of old score on the keyword

Sampling to reduce processing all search request.
- Since the system is both write and read heavy. We need to make it read heavy.
- We can use the concept of <b>sampling</b> to reduce the number of writes.
- Rather than maintaining scores for each request, we will sample only 10% of the request and discard rest of them.
- The probability of maintaining the same distribution will be nearly same had we processed all the request.
