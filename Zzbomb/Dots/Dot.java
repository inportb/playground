package Dots;

import com.jme3.bounding.BoundingSphere;
import com.jme3.math.Vector3f;
import com.jme3.scene.Geometry;
import com.jme3.scene.shape.Sphere;

public class Dot extends Dots {
	private float size = (float) 0.15;
	Vector3f loc;
	BoundingSphere sphereBounds;
	Sphere sphereMesh;
	Geometry sphere;

	public Dot(int x, int y, int z) {
		setLoc(new Vector3f(x, y, z));
		sphereBounds = new BoundingSphere((float)(size * 3), getLoc());
		sphereMesh = new Sphere(20, 20, 0.15f, true, true);
		sphere = new Geometry("Sky", sphereMesh);
	}
	
	// X
	public void setX(float x) {
		loc.x = x;
	}
	public float getX() {
		return loc.x;
	}
	// Y
	public void setY(float y) {
		loc.y = y;
	}
	public float getY() {
		return loc.y;
	}

	// Z
	public void setZ(float z) {
		loc.z = z;
	}
	public float getZ() {
		return loc.z;
	}

	public void setSphere(Geometry sphere) {
		this.sphere = sphere;
	}

	public Geometry getSphere() {
		return sphere;
	}

	public void setLoc(Vector3f loc) {
		this.loc = loc;
	}

	public Vector3f getLoc() {
		return loc;
		
	}
}
