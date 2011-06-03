package Dots;

import com.jme3.bounding.BoundingSphere;
import com.jme3.material.Material;
import com.jme3.math.Vector3f;
import com.jme3.scene.Geometry;
import com.jme3.scene.shape.Sphere;

public class Dot extends Dots {
	private int x;
	private int y;
	private int z;
	private int s;
	private float size = (float) 0.15;
	Vector3f loc;
	BoundingSphere sphereBounds;
	Sphere sphereMesh;
	Geometry sphere;

	public Dot(int x, int y, int z, int s) {
		setLoc(new Vector3f(x, y, z));
		this.s = s;
		sphereBounds = new BoundingSphere((float)(size * 3), getLoc());
		sphereMesh = new Sphere(20, 20, 0.15f, true, true);
		sphere = new Geometry("Sky", sphereMesh);
	}
	
	// X
	public void setX(int x) {
		this.x = x;
	}
	public int getX() {
		return x;
	}
	// Y
	public void setY(int y) {
		this.y = y;
	}
	public int getY() {
		return y;
	}

	// Z
	public void setZ(int z) {
		this.z = z;
	}
	public int getZ() {
		return z;
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
