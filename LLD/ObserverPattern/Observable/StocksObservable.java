package ObserverPattern.Observable;

import ObserverPattern.Observer.NotificationAlertObserver;
public interface StocksObservable{
    public void add(NotificationAlertObserver observer);
    public void remove(NotificationAlertObserver observer);
    public void notifySubscribers();
    public void setStockCount(int newStocks);
    public void getStockCount();
}