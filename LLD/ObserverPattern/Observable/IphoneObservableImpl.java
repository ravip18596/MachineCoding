package ObserverPattern.Observable;

import ObserverPattern.Observer.NotificationAlertObserver;
import java.util.ArrayList;
import java.util.List;
class IphoneObservableImpl implements StocksObservable{
    public List<NotificationAlertObserver> observerList = new ArrayList<>();
    public int stockCount = 0;

    public void add(NotificationAlertObserver observer){
        observerList.add(observer);
    }
    public void remove(NotificationAlertObserver observer){
        observerList.remove(observer);
    }
    public void notifySubscribers() {
        for (NotificationAlertObserver observer: observerList){
            observer.update();
        }
    }
    public void setStockCount(int newStock) {
        if stockCount == 0{
            notifySubscribers();
        }
        stockCount = stockCount + newStock;
    }

    public int getStockCount() {
        return stockCount;
    }


}