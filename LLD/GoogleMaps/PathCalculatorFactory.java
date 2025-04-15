package GoogleMaps;

public class PathCalculatorFactory {
    public static PathCalculator getPathCalculator(String mode) {
        if (mode.equals("Car")) {
            return new CarPathCalculator();
        } else if (mode.equals("Bike")) {
            return new BikePathCalculator();
        } else if (mode.equals("Walk")) {
            return new WalkPathCalculator();
        }
        return null;
    }
}