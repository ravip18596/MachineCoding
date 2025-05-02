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

## APIs

## Deep Dive

