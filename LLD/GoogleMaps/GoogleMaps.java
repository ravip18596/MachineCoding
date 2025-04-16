package GoogleMaps;

import GoogleMaps.PathCalculatorFactory;

public class GoogleMaps {
    public GoogleMaps(String mode, String src, String dest) {
        PathCalculator pathCalculator = PathCalculatorFactory.getPathCalculator(mode);
        pathCalculator.findPath(src, dest);
    }
    public static void main(String[] args) {

        GoogleMaps gm = new GoogleMaps("Car", "A", "B");
        GoogleMaps gm2 = new GoogleMaps("Bike", "A", "B");
        GoogleMaps gm3 = new GoogleMaps("Walk", "A", "B");
    }
}
