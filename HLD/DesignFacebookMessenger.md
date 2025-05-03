# Facebook Messenger

## Functional Requirements

- We will support 1:1 user chat
- Support read and write of chat messages
- Support showing all the conversations of the user

## Non Functional Requirements
- Consistency vs Availability
- Low latency vs consistency

## Back of the envelope calculations

RPS

Storage

## APIs
- getUserConversations(user_id)
- getMessages(conversation_id)
- writeMessages(conversation_id)
  
## Deep Dive

1. Sharding key will be <b>user_id</b> if only 1:1 user chatting allowed
2. Sharding key will be <b>conversation_id</b> if group chatting is also allowed

Modes of communications between client and server
1. polling
   - Pros:
   - Cons:
      - This method consumes client's resources
      - This method also consumes server RAM
3. long polling
   - Pros:
   - Cons:
      - This method also consumes server RAM
4. web sockets
   - Pros:
      - It is a 2 way communication strategy between client and server
      - It needs to be established only once.
   - Cons:
      - This method also consumes server RAM
