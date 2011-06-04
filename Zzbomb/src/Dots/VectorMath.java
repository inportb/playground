package Dots;

import com.jme3.math.Vector3f;

/**
 * @author John Spaetzel <john.spaetzel@gmail.com>
 * @version 1.0
 * @since 1.6
 */
public class VectorMath {

	/**
	 * Determine distance between two points
	 * 
	 * @param a
	 *            The first point
	 * @param b
	 *            The second point
	 * @return Returns a double variable of the distance between the inputted
	 *         points.
	 */
	public static double EuclideanDistance(Vector3f a, Vector3f b) {
		return Math.sqrt(Math.pow(b.getX() - a.getX(), 2) + Math.pow(b.getY() - a.getY(), 2) + Math.pow(b.getZ() - a.getZ(), 2));
	}

	/**
	 * Four Vectors to determine if two lines are parallel.
	 * 
	 * @return Boolean true if lines are parallel
	 */
	public static boolean isParallel(Vector3f a, Vector3f b, Vector3f a1, Vector3f b1) {
		// ab is line 1
		// a1 b1 is line 2
		if (a != a1 && b != b1)
		// No comparing the same line....
		{
			if (EuclideanDistance(a, b1) == EuclideanDistance(b, a1) && EuclideanDistance(a, b) == 1 && EuclideanDistance(a1, b1) == 1
					&& EuclideanDistance(a, a1) == EuclideanDistance(b, b1)) {
				// Horizontal Lines
				if (EuclideanDistance(a, a1) == 1.0 && EuclideanDistance(b, b1) == 1.0) {
					return true;
				}
				// Vertical Lines
				if (EuclideanDistance(a, b1) == 1.0 && EuclideanDistance(b, a1) == 1.0) {
					return true;
				}
			}
		}
		return false;
	}
	
	public static boolean compareVectors(Vector3f a, Vector3f b) {
		if ( a.getX() == b.getX() && a.getY() == b.getY() && a.getZ() == b.getZ() ) {
			return true;
		}
		return false;
	}
	
	public static void printVector3f( Vector3f a ) {
		System.out.println("X: " + a.getX() + " Y: " + a.getY() + " Z: " + a.getZ());
	}
}
