import cv2
import numpy as np
import pickle
import os

class PolylineManager:
    def __init__(self):
        self.polylines = []  # Stores all drawn polylines
        self.polyline_names = []  # Stores names of the polylines
        self.current_points = []  # Holds points for the current polyline
        self.pickle_file = "polylines.pkl"  # Filename for saved polylines
        self.load_polylines()  # Load any existing polylines

    def load_polylines(self):
        """Load saved polylines and names from pickle file if it exists."""
        if os.path.exists(self.pickle_file):
            with open(self.pickle_file, 'rb') as file:
                self.polylines, self.polyline_names = pickle.load(file)

    def save_polylines(self):
        """Save current polylines and names to a pickle file."""
        with open(self.pickle_file, 'wb') as file:
            pickle.dump((self.polylines, self.polyline_names), file)

    def clear_polylines(self):
        """Clear all polylines, names, and delete the pickle file."""
        self.polylines.clear()
        self.polyline_names.clear()
        if os.path.exists(self.pickle_file):
            os.remove(self.pickle_file)

    def add_point(self, point):
        """Add a point to the current polyline being drawn."""
        if len(self.current_points) < 4:  # Limit to 4 points for closed polygon
            self.current_points.append(point)

    def draw_polylines(self, frame):
        """Draw all saved polylines and active points on the given frame."""
        for polyline in self.polylines:
            if len(polyline) >= 4:
                cv2.polylines(frame, [np.array(polyline)], isClosed=True, color=(255, 0, 0), thickness=2)
        for point in self.current_points:
            cv2.circle(frame, point, 5, (0, 0, 255), -1)
        return frame

    def get_polyline_names(self):
        """Return names of all saved polylines."""
        return self.polyline_names

    def is_point_in_polyline(self, point, polyline_name):
        """Check if a point is inside a polyline specified by name."""
        if polyline_name in self.polyline_names:
            index = self.polyline_names.index(polyline_name)
            polyline = self.polylines[index]
            polyline_array = np.array(polyline, dtype=np.int32)
            return cv2.pointPolygonTest(polyline_array, point, False) >= 0
        return False

    def handle_key_events(self):
        """Manage key events for saving, clearing, or exiting."""
        key = cv2.waitKey(1) & 0xFF
        if key == ord("e"):
            return False
        elif key == ord("s"):
            self.save_polylines()
        elif key == ord("d"):
            self.clear_polylines()
        elif len(self.current_points) == 4:
            polyline_name = input("Enter a name for the polyline: ")
            self.polyline_names.append(polyline_name)
            self.polylines.append(self.current_points.copy())
            self.current_points.clear()
        return True