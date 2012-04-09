package Dots;

import java.util.logging.Level;
import java.util.logging.Logger;

import Dots.Dot;
import Dots.Vector3fMath;

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
import com.jme3.system.AppSettings;

public class Dots extends SimpleApplication {
	// Initial Parameters
	static int s = 5; // How large should the grid be?
	private int playerCount = 2; // How many players are there?

	// Secondary Parameters
	Vector3f[] selected = new Vector3f[2];
	private static Dot grid[][][] = new Dot[s][s][s];
	private int player = 0; // Current Players Turn.
	private static int LineCount = 0; // Total Count of Lines Played in Game.

	// Storage Variables
	private static int selectCount = 0; // Temporary Storage Variable
	private static Vector3f Lines[][] = new Vector3f[s * s * s * 6][2]; // LinesArchive
	private int pScore[] = new int[playerCount];

	// Global Hud Variables for updating.
	private static BitmapText hudText;
	private static Geometry HudPlayerTurnGeo;

	// Global Color Materials
	Material blue, green, red, yellow, white;

	// Find a way to not need this...
	private static Vector3f reset = new Vector3f(1, 2, 3);

	public static void main(String[] args) {
		Logger.getLogger("").setLevel(Level.SEVERE); // Stop JME3 Outputs
		Dots app = new Dots();
		app.setShowSettings(false); // Dont display Splash Window
		
		AppSettings appset = new AppSettings(true); // Define Settings of Application
		appset.setResolution(1024, 800);
		appset.setTitle("DOTS, 3D by John Spaetzel");
		appset.setRenderer(AppSettings.LWJGL_OPENGL_ANY);
		appset.setVSync(true);
		app.setSettings(appset);
		
		app.start();
	}

	// Initializes the App
	@Override
	public void simpleInitApp() {
		Node Board = new Node(); // Create 3d Plane
		rootNode.attachChild(Board); // Attach 3d Plan to rootNode

		flyCam.setMoveSpeed(4); // Increase camera movement speed.

		// Configure Colors, with Semi-Transparency.
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

		// Initialize the game heads up display.
		initHud();

		// Initialize the grid.
		for (int i = 0; i < s; i++) {
			for (int f = 0; f < s; f++) {
				for (int k = 0; k < s; k++) {
					grid[i][f][k] = new Dot(i, f, k); // Create a dot
					grid[i][f][k].getSphere().setMaterial(white); // Set the
					// dot's
					// material
					grid[i][f][k].getSphere()
							.setQueueBucket(Bucket.Transparent); // transparency
					Board.attachChild(grid[i][f][k].getSphere()); // Attach dot
					// to board
					grid[i][f][k].getSphere().setLocalTranslation(
							grid[i][f][k].getLoc()); // Set location of dot
				}
			}
		}

		// Reset Player Scores for new game
		for (int i = 0; i < playerCount; i++) {
			pScore[i] = 0;
		}

		inputManager.addMapping("MouseDown", new MouseButtonTrigger(
				MouseInput.BUTTON_LEFT));
		inputManager.addListener(actionListener, new String[] { "MouseDown" });
	}

	// Initialized the HUD
	private void initHud() {
		// CROSSHAIRS
		guiNode.detachAllChildren();
		guiFont = assetManager.loadFont("Interface/Fonts/Default.fnt");
		BitmapText ch = new BitmapText(guiFont, false);
		ch.setSize(guiFont.getCharSet().getRenderedSize() * 2);
		ch.setText("+"); // fake crosshairs :)
		ch.setLocalTranslation(
				// center
				settings.getWidth() / 2
						- guiFont.getCharSet().getRenderedSize() / 3 * 2,
				settings.getHeight() / 2 + ch.getLineHeight() / 2, 0);

		// HUD TEXT
		hudText = new BitmapText(guiFont, false);
		hudText.setSize(guiFont.getCharSet().getRenderedSize()); // font size
		hudText.setColor(ColorRGBA.Orange); // font color

		// HUD PLAYER BAR
		Quad guiPlayerTurnQuad = new Quad((settings.getWidth() / 28), settings
				.getHeight());
		HudPlayerTurnGeo = new Geometry("PlayerTurn", guiPlayerTurnQuad);
		HudPlayerTurnGeo.setMaterial(blue);

		guiNode.attachChild(ch); // Attach Crosshairs
		guiNode.attachChild(hudText); // Attach HudText
		guiNode.attachChild(HudPlayerTurnGeo); // Attach PlayerTurnGeo

		updateHud();
		hudText.setLocalTranslation(0, hudText.getHeight(), 0); // Repostition
		// HudText for
		// size.
		HudPlayerTurnGeo.setLocalTranslation(settings.getWidth()
				- settings.getWidth() / 28, 1, 1); // Reposition playerturnquad

	}

	// Refreshes the HUD with latest data.
	private void updateHud() {
		hudText.setText("Player Blue: " + pScore[0] + "\nPlayer Red: "
				+ pScore[1]); // Update Text
		// Update Player indicator
		if (player == 0) {
			HudPlayerTurnGeo.setMaterial(blue);
		} else if (player == 1) {
			HudPlayerTurnGeo.setMaterial(red);
		} else {
			// This should not be possible. But will currently happen if there
			// are more then 2 players. Failsafe.
			HudPlayerTurnGeo.setMaterial(white);
			System.out
					.println("Woa. Too many players. Dots has not been programmed for more then two yet.");
		}
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

					int tmpx = (int) closest.getGeometry()
							.getLocalTranslation().getX();
					int tmpy = (int) closest.getGeometry()
							.getLocalTranslation().getY();
					int tmpz = (int) closest.getGeometry()
							.getLocalTranslation().getZ();
					
						/*
						 * 1. On First selection.
						 * 		A. Make selected dot yellow
						 * 2. On Second selection.
						 * 		A. Can a line exist there? - No? Reset Selection Process
						 *		B. Does a line already exist there? - Yes? Reset Selection Process
						 *		C. Everything checks out. Draw the line.
						 *			1. Was a square completed? - No? Change Players
						 *			2. Yes? Dont change players, increase current player score by 1.
						 * 3. Reset Selections
						 **/
					
					if (selectCount == 0 )	{
						selected[0] = new Vector3f(tmpx, tmpy, tmpz); // First selection made.
						SetSphereColor(selected[0], "yellow"); // Set to yellow.
						selectCount++;
					} else if ( selectCount == 1 ) {
						selected[1] = new Vector3f(tmpx,tmpy,tmpz); // Second selection made.
						// Only accept this selection if a line does not already exist there. AND distance is ok.
						if (LineExist(selected[0], selected[1], Lines,
								LineCount) == false && Vector3fMath.EuclideanDistance(selected[0], selected[1]) <= 1 ) {
							selectCount++;
						}
						else {
							resetSelections();
						}
					} else {
						resetSelections();
					}
					
					// If two selection have been properly made.. Time to do some fun stuff.
					if ( selectCount == 2 ) {
						drawPrep(); // Draws the line.
						
						// Record lines in archive.
						Lines[LineCount][0] = selected[0];
						Lines[LineCount][1] = selected[1];
						LineCount++;
						
						// Check for a square!
						if ( CheckForSquare(selected, Lines, LineCount) ) {
							pScore[player]++; // Nifty that player got a square. Give them a point
						} 
						// If a square was not scored, player needs to be changed. This will work with more then 2 players.
						else if ( player < playerCount-1 ) {
							player++;
						} else { 
							player = 0;
						}
						updateHud(); // Update HUD for any point changes and such.
						resetSelections(); // Next selection can be made.
					}
				}
			}
		}
	};
	
	// Determine how and where to draw the line.
	// This is for up/down/left/right offsets and nonsuch.
	private void drawPrep() {
		if (selected[0].getX() == selected[1].getX() - 1) {
			drawConnector(new Vector3f((float) (selected[1].getX() + 0.40), selected[1].getY(), selected[1].getZ() ));

		} else if (selected[0].getX() == selected[1].getX() + 1) {
			drawConnector(new Vector3f((float) (selected[1].getX() - 0.40), selected[1].getY(), selected[1].getZ() ));
		}

		// Y

		else if (selected[0].getY() == selected[1].getY() + 1) {
			drawConnector(new Vector3f(selected[1].getX(), (float) (selected[1].getY() + 0.40), selected[1].getZ()));
		} else if (selected[0].getY() == selected[1].getY() - 1) {
			drawConnector(new Vector3f(selected[1].getX(), (float) (selected[1].getY() - 0.40), selected[1].getZ()));
		}

		// Z

		else if (selected[0].getZ() == selected[1].getZ() + 1) {
			drawConnector(new Vector3f(selected[1].getX(), selected[1].getY(), (float) (selected[1].getZ() + 0.40)));
		} else if (selected[0].getZ() == selected[1].getZ() - 1) {
			drawConnector(new Vector3f(selected[1].getX(), selected[1].getY(), (float) (selected[1].getZ() - 0.40)));
		}
	}
	
	// Draws the line.
	private void drawConnector(Vector3f loc) {
		Line connect = new Line(selected[0], selected[1]);
		connect.setLineWidth(20f);
		Geometry line = new Geometry("Sky", connect);
		if ( player == 0 ) {
			line.setMaterial(blue);
		} else if ( player == 1 ) {
			line.setMaterial(red);
		} else {
			line.setMaterial(white);
			// Currently not setup for more then two players.
		}
		line.setQueueBucket(Bucket.Transparent);
		rootNode.attachChild(line);
	}
	
	// Set the color of a specified dot.
	private void SetSphereColor(Vector3f vector, String color) {
		if (color == "yellow") {
			grid[(int) vector.getX()][(int) vector.getY()][(int) vector.getZ()]
					.getSphere().setMaterial(yellow);
		} else if (color == "white") {
			grid[(int) vector.getX()][(int) vector.getY()][(int) vector.getZ()]
					.getSphere().setMaterial(white);
		}

	}
	

	/*
	 * Determine if a square exists in in the Lines array based on two initial points.
	 */
	private boolean CheckForSquare(Vector3f[] Selected, Vector3f[][] Lines, int LineCount) {
		for (int i = 0; i < LineCount; i++) {
			// Compare the selected line against all lines in the Lines array.
			// True if it finds a parallel line one away.
			if (Vector3fMath.isParallel(Selected[0], Selected[1], Lines[i][0], Lines[i][1])) {	
				if (LineExist(Selected[0], Lines[i][0], Lines, LineCount) && LineExist(Selected[1], Lines[i][1], Lines, LineCount)) {
					return true;
				}
				if (LineExist(Selected[0], Lines[i][1], Lines, LineCount) && LineExist(Selected[1], Lines[i][0], Lines, LineCount)) {
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
			if ( Vector3fMath.equalVectors(Lines[i][0], a) && Vector3fMath.equalVectors(Lines[i][1], b) ) {
				return true;
			}
			if ( Vector3fMath.equalVectors(Lines[i][0], b) && Vector3fMath.equalVectors(Lines[i][1], a) ) {
				return true;
			}
		}
		return false;
	}
	
	private void resetSelections() {
		 	selectCount = 0;
			SetSphereColor(selected[0], "white");
			selected[0] = reset;
			selected[1] = reset;
	}
}