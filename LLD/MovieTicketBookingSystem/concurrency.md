Question
--------
How to make sure no two users book the same seat? 

Solution
---------
We can use transactions in SQL database.
- Within a transaction, if we read rows we get a write-lock on them so that they can't be updated by anybpdy else.

- Highest level of transaction isolation level is Serializable

```sql
SET TRANSACTION ISOLATION LEVEL SERIALISABLE;

Begin Transaction;

select * from showSeat where show_id = 90 and seat_id in (55, 56, 57) and isReserved=0;

-- if the number of rows returned by the above statement is NOT three, we can return failure to the user.

update ShowSeat table ...
update Booking table ...

Commit Transaction;
```

- Once the transaction is successful, we can safely assume that reservation is also successful.