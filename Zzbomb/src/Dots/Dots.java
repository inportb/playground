package Dots;

import java.util.logging.Level;
import java.util.logging.Logger;

import com.jme3.app.SimpleApplication;
import com.jme3.collision.CollisionResult;
import com.jme3.collision.CollisionResults;
import com.jme3.font.BitmapText;
import com.jme3.input.MouseInput;
import com.jme3.input.controls.ActionListener;
import com.jme3.input.controls.MouseButtonTrigger;
import com.jme3.material.Material;
import com.jme3.material.RenderState.BlendMode;
import com.jme3.math.ColorRGBA;
import com.jme3.math.Ray;
import com.jme3.math.Vector3f;
import com.jme3.renderer.queue.RenderQueue.Bucket;
import com.jme3.scene.Geometry;
import com.jme3.scene.Node;
import com.jme3.scene.shape.Line;
import com.jme3.scene.shape.Quad;

import Dots.VectorMath;

public class Dots extends SimpleApplication {

	private static int s = 4; // How large should the grid be?
	private static int selectCount = 0; // Temporary Storage Variable
	Vector3f[] selected = new Vector3f[2];
	private static Dot grid[][][] = new Dot[s][s][s];
	private  int player = 0;
	private  int playerCount = 2;
	private  int pScore[] = new int[playerCount];
	private static Vector3f Lines[][] = new Vector3f[s * s * s * 6][2]; // Vector
																		// containing
																		// line
																		// archive
	private static int LineCount = 0; // Permanent Storage Variable.
	private static BitmapText hudText;
	private static Vector3f reset = new Vector3f(1, 2, 3);
	Material blue, green, red, yellow, white;

	public static void main(String[] args) {
		Logger.getLogger("").setLevel(Level.SEVERE);
		Dots app = new Dots();
		app.start();
	}
	
	@Override
	public void simpleInitApp() {
		Node Board = new Node();
		rootNode.attachChild(Board);

		initCrossHairs();
		initHud();
		flyCam.setMoveSpeed(4);
		blue = new Material(assetManager, "Common/MatDefs/Misc/Unshaded.j3md");
		blue.setColor("Color", new ColorRGBA(0, 0, 1, 0.4f));
		blue.getAdditionalRenderState().setBlendMode(BlendMode.Alpha);

		green = new Material(assetManager, "Common/MatDefs/Misc/Unshaded.j3md");
		green.setColor("Color", new ColorRGBA(0.0f, 1.0f, 0.0f, 0.50f));
		green.getAdditionalRenderState().setBlendMode(BlendMode.Alpha);

		red = new Material(assetManager, "Common/MatDefs/Misc/Unshaded.j3md");
		red.setColor("Color", new ColorRGBA(1.0f, 0.0f, 0.0f, 0.50f));
		red.getAdditionalRenderState().setBlendMode(BlendMode.Alpha);

		yellow = new Material(assetManager, "Common/MatDefs/Misc/Unshaded.j3md");
		yellow.setColor("Color", new ColorRGBA(1.0f, 1.0f, 0.0f, 0.50f));
		yellow.getAdditionalRenderState().setBlendMode(BlendMode.Alpha);

		white = new Material(assetManager, "Common/MatDefs/Misc/Unshaded.j3md");
		white.setColor("Color", new ColorRGBA(1.0f, 1.0f, 1.0f, 0.50f));
		white.getAdditionalRenderState().setBlendMode(BlendMode.Alpha);

		for (int i = 0; i < s; i++) {
			for (int f = 0; f < s; f++) {
				for (int k = 0; k < s; k++) {
					grid[i][f][k] = new Dot(i, f, k, s);
					grid[i][f][k].setX(i);
					grid[i][f][k].setY(f);
					grid[i][f][k].setZ(k);
					grid[i][f][k].getSphere().setMaterial(white);

					grid[i][f][k].getSphere().setQueueBucket(Bucket.Transparent);
					Board.attachChild(grid[i][f][k].getSphere());
					grid[i][f][k].getSphere().setLocalTranslation(grid[i][f][k].getLoc());
				}
			}
		}
		pScore[0] = 0;
		pScore[1] = 0;
		
		inputManager.addMapping("MouseDown", new MouseButtonTrigger(MouseInput.BUTTON_LEFT));
		inputManager.addListener(actionListener, new String[] { "MouseDown" });
	}

	private void initHud() {
		hudText = new BitmapText(guiFont, false);
		hudText.setSize(guiFont.getCharSet().getRenderedSize()); // font size
		hudText.setColor(ColorRGBA.Orange); // font color
		updateHud();
		hudText.setLocalTranslation(0, hudText.getHeight(), 0); // position
		guiNode.attachChild(hudText);
	}

	private boolean CheckSelectedDistance() {
		if (VectorMath.EuclideanDistance(selected[0], selected[1]) <= 1) {
			return true;
		} else {
			return false;
		}
	}

	private void chknear(int x, int y, int z) {
		float xf = x;
		float yf = y;
		float zf = z;

		// Is one already selected? Is the 2nd point within clicking distance?
		if (selectCount > 1 && CheckSelectedDistance() == true) {

			// X

			if (selected[0].getX() == xf - 1) {
				drawConnector(new Vector3f((float) (xf + 0.40), yf, zf));

			} else if (selected[0].getX() == xf + 1) {
				drawConnector(new Vector3f((float) (xf - 0.40), yf, zf));
			}

			// Y

			else if (selected[0].getY() == yf + 1) {
				drawConnector(new Vector3f(xf, (float) (yf + 0.40), zf));
			} else if (selected[0].getY() == yf - 1) {
				drawConnector(new Vector3f(xf, (float) (yf - 0.40), zf));
			}

			// Z

			else if (selected[0].getZ() == zf + 1) {
				drawConnector(new Vector3f(xf, yf, (float) (zf + 0.40)));
			} else if (selected[0].getZ() == zf - 1) {
				drawConnector(new Vector3f(xf, yf, (float) (zf - 0.40)));
			}

		}
	}

	private void drawConnector(Vector3f loc) {
		Line connect = new Line(selected[0], selected[1]);
		connect.setLineWidth(20f);
		Geometry line = new Geometry("Sky", connect);
		line.setMaterial(blue);
		line.setQueueBucket(Bucket.Transparent);
		rootNode.attachChild(line);
		for (int i = 0; i < 2; i++) {
			SetSphereColor(selected[i], "white");
		}
		// Wow. Ok so the connector was just drawn. Its time to figure out if we
		// need to draw anything else....
		Lines[LineCount][0] = selected[0];
		Lines[LineCount][1] = selected[1];
		LineCount++;
		if ( CheckSquare(selected, Lines, LineCount, s) ) {
			System.out.println("Lol a square exists");
			pScore[player]++;
		}
		// Update who's turn it is now that the line has been drawn.
		if ( player < playerCount-1 ) {
			player++;
		}
		else {
			player = 0;
		}
		updateHud();
	}

	private void updateHud()
	{
		hudText.setText("Player 1: " + pScore[0] + "\nPlayer 2: " + pScore[1] + "\nLineCount: " + LineCount + "\nPlayer Turn: " + (player+1) );
	}
	
	private ActionListener actionListener = new ActionListener() {
		public void onAction(String name, boolean keyPressed, float tpf) {
			if (name.equals("MouseDown") && !keyPressed) {

				CollisionResults results = new CollisionResults();
				Ray ray = new Ray(cam.getLocation(), cam.getDirection());

				rootNode.collideWith(ray, results);

				if (results.size() > 0) {

					// The closest collision point is what was truly hit:
					CollisionResult closest = results.getClosestCollision();

					int tmpx = (int) closest.getGeometry().getLocalTranslation().getX();
					int tmpy = (int) closest.getGeometry().getLocalTranslation().getY();
					int tmpz = (int) closest.getGeometry().getLocalTranslation().getZ();

					if (selectCount < 2) {
						selected[selectCount] = new Vector3f(tmpx, tmpy, tmpz);
						if ( LineExist(selected[0], selected[1], Lines, LineCount) == false  ) {
							selectCount++;
						}
						else {
							resetSelected();
						}
					} else {
						selectCount = 0;
						for (int i = 0; i < 2; i++) {
							SetSphereColor(selected[i],"white");
							selected[i] = reset;
						}

						selected[selectCount] = new Vector3f(tmpx, tmpy, tmpz);
					}
					if (selectCount > 0 && selectCount <= 2) {
						if (selectCount == 1) {
							// First Selection.
							SetSphereColor(selected[0], "yellow");
						} else if (selectCount == 2) {
							// Second Selection
							if (CheckSelectedDistance()) {
								SetSphereColor(selected[1], "yellow");
							} else {
								SetSphereColor(selected[0], "white");
								selected[0] = reset;
							}

							chknear((int) selected[1].getX(), (int) selected[1].getY(), (int) selected[1].getZ());
							resetSelected();
						}
					}
				}
			}
		}
	};

	private void resetSelected () {
		selectCount = 0;
		SetSphereColor(selected[0], "white");
		SetSphereColor(selected[1], "white");
		selected[0] = reset;
		selected[1] = reset;
		
	}
	
	private void drawQuad(Vector3f a, Vector3f b, Vector3f a1, Vector3f b1) {
		Quad quadshape = new Quad(1f, 1f);
		Geometry quad = new Geometry("quad", quadshape);
		Material mat_stl = new Material(assetManager, "Common/MatDefs/Misc/Unshaded.j3md");
		quad.setMaterial(blue);
		quad.setQueueBucket(Bucket.Transparent);
		quad.setLocalTranslation(a);
		rootNode.attachChild(quad);
	}

	protected void SetSphereColor(Vector3f vector, String color) {
		if (color == "yellow") {
			grid[(int) vector.getX()][(int) vector.getY()][(int) vector.getZ()].getSphere().setMaterial(yellow);
		} else if (color == "white") {
			grid[(int) vector.getX()][(int) vector.getY()][(int) vector.getZ()].getSphere().setMaterial(white);
		}

	}

	public boolean CheckSquare(Vector3f[] Selected, Vector3f[][] Lines, int LineCount, int s) {
		if (CheckForSquare(Selected[0], Selected[1], Lines, LineCount)) {
			return true;
		}
		else {
			return false;
		}
	}

	/*
	 * Determine if a square exists in in the Lines array based on two initial points.
	 */
	private boolean CheckForSquare(Vector3f a, Vector3f b, Vector3f[][] Lines, int LineCount) {
		for (int i = 0; i < LineCount; i++) {
			// Compare the selected line against all lines in the Lines array.
			// True if it finds a parallel line one away.
			if (VectorMath.isParallel(a, b, Lines[i][0], Lines[i][1])) {	
				if (LineExist(a, Lines[i][0], Lines, LineCount) && LineExist(b, Lines[i][1], Lines, LineCount)) {
					return true;
				}
				if (LineExist(a, Lines[i][1], Lines, LineCount) && LineExist(b, Lines[i][0], Lines, LineCount)) {
					return true;
				}
				
			}
		}		
		return false;
	}

	/*
	 *  Shows if a line of a,b exists in the lines array.
	 */
	private static boolean LineExist(Vector3f a, Vector3f b, Vector3f[][] Lines, int LineCount) {
		for ( int i = 0; i < LineCount; i++ ) {
			if ( VectorMath.compareVectors(Lines[i][0], a) && VectorMath.compareVectors(Lines[i][1], b) ) {
				return true;
			}
			if ( VectorMath.compareVectors(Lines[i][0], b) && VectorMath.compareVectors(Lines[i][1], a) ) {
				return true;
			}
		}
		return false;
	}
	
	
	protected void initCrossHairs() {
		guiNode.detachAllChildren();
		guiFont = assetManager.loadFont("Interface/Fonts/Default.fnt");
		BitmapText ch = new BitmapText(guiFont, false);
		ch.setSize(guiFont.getCharSet().getRenderedSize() * 2);
		ch.setText("+"); // fake crosshairs :)
		ch.setLocalTranslation(
				// center
				settings.getWidth() / 2 - guiFont.getCharSet().getRenderedSize() / 3 * 2,
				settings.getHeight() / 2 + ch.getLineHeight() / 2, 0);
		guiNode.attachChild(ch);
	}

}