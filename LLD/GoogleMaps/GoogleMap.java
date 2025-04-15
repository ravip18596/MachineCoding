package GoogleMaps;

public class GoogleMap {
    public GoogleMap(String mode, String src, String dest) {
        PathCalculator pathCalculator = PathCalculatorFactory.getPathCalculator("Car");
        pathCalculator.findPath("A", "B");

        PathCalculator pc2 = PathCalculatorFactory.getPathCalculator("Bike");
        pc2.findPath("A", "B");

        PathCalculator pc3 = PathCalculatorFactory.getPathCalculator("Walk");
        pc3.findPath("A", "B");
    }
    public static void main(String[] args) {
        GoogleMap gm = new GoogleMap("Car", "A", "B");
    }
}
