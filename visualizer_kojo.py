import os
from datetime import datetime
import numpy as np
import time
import cv2
from timer import Timer
import csv  # Add this import for CSV handling

from skin_sensor import TactileSkin

text_display = False
color_enhance = 1#1.5
activation_threshold = 100
# Flag to track if the "guess.png" image should be displayed
display_guess_image = False
guess_image = cv2.imread("guess.png")

# def write_to_csv_with_timestamp(data, filename):
#     timestamp = round(time.time() - start, 2)  # Calculate elapsed time in seconds
#     data_with_timestamp = [timestamp] + list(data)  # Add timestamp as the first element
#     with open(filename, 'a', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(data_with_timestamp)

def write_to_csv_with_timestamp_and_headers(data, filename, headers):
    timestamp = round(time.time() - start, 2)
    data_with_timestamp = [timestamp] + list(data)
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write headers if the file is empty
        if os.stat(filename).st_size == 0:
            writer.writerow(headers)
        writer.writerow(data_with_timestamp)

def heatMap(tactile_data, rows, cols, show_colorbar=True):
    unit_w = 80
    unit_h = 80
    min_v = 0
    max_v = 1024

    def map_color(value):
        if value < 0.25:
            return (0, 0, int(255 * (value / 0.25)))
        elif value < 0.5:
            return (0, int(255 * ((value - 0.25) / 0.25)), 255)
        elif value < 0.75:
            return (int(255 * ((value - 0.5) / 0.25)), 255, 0)
        else:
            return (255, int(255 * (1 - (value - 0.75) / 0.25)), 0)

    data_array = tactile_data.reshape((rows, cols))
    #data_array = tactile_data.reshape((rows, cols), order='F')
    img_array = np.zeros((unit_h * rows, unit_w * cols, 3), dtype=np.uint8)

    for i in range(rows):
        for j in range(cols):
            normalized_value = (data_array[i, j] - min_v) / (max_v - min_v)
            color = map_color(1 - normalized_value)
            img_array[i * unit_h:(i + 1) * unit_h, j * unit_w:(j + 1) * unit_w, :] = color

            if text_display:
                font = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 1
                text_color = (255, 255, 255)
                thickness = 2
                text = str(data_array[i, j])
                text_size = cv2.getTextSize(text, font, fontScale, thickness)[0]
                text_x = j * unit_w + (unit_w - text_size[0]) // 2
                text_y = i * unit_h + (unit_h + text_size[1]) // 2
                cv2.putText(img_array, text, (text_x, text_y), font, fontScale, text_color, thickness, cv2.LINE_AA)

    if show_colorbar:
        color_bar = np.zeros((unit_h * rows, 30, 3), dtype=np.uint8)
        for i in range(unit_h * rows):
            normalized_value = 1 - i / (unit_h * rows)
            color = map_color(1 - normalized_value)
            color_bar[i, :, :] = color

        img_array = np.hstack((img_array, color_bar))

    return img_array

if __name__ == '__main__':
    rows = 8#8
    cols = 8#8
    timer = Timer()
    tactile_recorder = TactileSkin(serialPort="COM3", serialBaud=57600)
    time.sleep(1.0)

    # Specify the CSV file name
    csv_filename = 'results1.csv'
    column_headers = ["Time"] + [f"T{i}" for i in range(1, rows * cols + 1)]


    print("Start streaming tactile data...")
    start = time.time()

    show_colorbar = True
    text_display = False
    displaying_image = False
    image_start_time = None

    # Determine the position for the "Guess" image
    guess_window_x = 200
    guess_window_y = 0

    # Determine the position for the "Happy Halloween" image (adjust as needed)
    halloween_window_x = guess_window_x
    halloween_window_y = guess_image.shape[0]  # Position it below the "Guess" image
    t1=0
    for i in range(10000):
        timestamp = timer.time
        tactile_data = tactile_recorder.readData()
        tactile_data = tactile_data[:-2].split(" ")[:-1]
        #print(1/(time.time()-t1)) #time algo
        t1 = time.time()
        try:
            tactile_data = np.array([int(item) for item in tactile_data])
        except:
            print("Data error!")
            continue

        if len(tactile_data) != rows * cols:
            continue

        tactile_data = np.where(tactile_data < 0, 0, tactile_data)

        # Write data to CSV file
        write_to_csv_with_timestamp_and_headers(tactile_data, csv_filename, column_headers)

        tactile_img = heatMap(tactile_data * color_enhance, rows, cols, show_colorbar)
        cv2.imshow('Tactile reading', tactile_img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Quitting the data collection...")
            break

        # Toggle the colorbar display on 'c' key press
        elif key == ord('c'):
            show_colorbar = not show_colorbar

        # Toggle the text display on 't' key press
        elif key == ord('t'):
            text_display = not text_display

        elif key == ord('d'):
            if not display_guess_image:
                cv2.namedWindow('Guess', cv2.WINDOW_NORMAL)
                cv2.moveWindow('Guess', guess_window_x, guess_window_y)
                cv2.imshow('Guess', guess_image)
                display_guess_image = True
            else:
                cv2.destroyWindow('Guess')
                display_guess_image = False

        # # Check if taxel units R1C1, R8C1, and R8C8 are pressed for more than 4 seconds
        # if tactile_data[56] > activation_threshold and tactile_data[63] > activation_threshold:
        #     if not displaying_image:
        #         image_start_time = time.time()
        #         displaying_image = True

        #     # Load and display the "happy_halloween.png" image
        #     if displaying_image:
        #         image = cv2.imread("happy_halloween6.png")
        #         cv2.namedWindow('Happy Halloween', cv2.WINDOW_NORMAL)
        #         cv2.moveWindow('Happy Halloween', halloween_window_x, halloween_window_y+20)
        #         cv2.imshow('Happy Halloween', image)

        #     if displaying_image and (time.time() - image_start_time) > 4:
        #         cv2.waitKey(4)  # Wait for 4 seconds
        #         cv2.destroyWindow('Happy Halloween')
        #         displaying_image = False

    end = time.time()
    print("Ended!", (end - start))

cv2.destroyAllWindows()


# import os
# from datetime import datetime
# import numpy as np
# import time
# import cv2
# from timer import Timer
# import csv  # Add this import for CSV handling

# from skin_sensor import TactileSkin

# text_display = False
# color_enhance = 1#1.5
# activation_threshold = 100
# # Flag to track if the "guess.png" image should be displayed
# display_guess_image = False
# guess_image = cv2.imread("guess.png")

# def write_to_csv(data, filename):
#     with open(filename, 'a', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(data)

# def heatMap(tactile_data, rows, cols, show_colorbar=True):
#     unit_w = 80
#     unit_h = 80
#     min_v = 0
#     max_v = 1024

#     def map_color(value):
#         if value < 0.25:
#             return (0, 0, int(255 * (value / 0.25)))
#         elif value < 0.5:
#             return (0, int(255 * ((value - 0.25) / 0.25)), 255)
#         elif value < 0.75:
#             return (int(255 * ((value - 0.5) / 0.25)), 255, 0)
#         else:
#             return (255, int(255 * (1 - (value - 0.75) / 0.25)), 0)

#     data_array = tactile_data.reshape((rows, cols))
#     #data_array = tactile_data.reshape((rows, cols), order='F')
#     img_array = np.zeros((unit_h * rows, unit_w * cols, 3), dtype=np.uint8)

#     for i in range(rows):
#         for j in range(cols):
#             normalized_value = (data_array[i, j] - min_v) / (max_v - min_v)
#             color = map_color(1 - normalized_value)
#             img_array[i * unit_h:(i + 1) * unit_h, j * unit_w:(j + 1) * unit_w, :] = color

#             if text_display:
#                 font = cv2.FONT_HERSHEY_SIMPLEX
#                 fontScale = 1
#                 text_color = (255, 255, 255)
#                 thickness = 2
#                 text = str(data_array[i, j])
#                 text_size = cv2.getTextSize(text, font, fontScale, thickness)[0]
#                 text_x = j * unit_w + (unit_w - text_size[0]) // 2
#                 text_y = i * unit_h + (unit_h + text_size[1]) // 2
#                 cv2.putText(img_array, text, (text_x, text_y), font, fontScale, text_color, thickness, cv2.LINE_AA)

#     if show_colorbar:
#         color_bar = np.zeros((unit_h * rows, 30, 3), dtype=np.uint8)
#         for i in range(unit_h * rows):
#             normalized_value = 1 - i / (unit_h * rows)
#             color = map_color(1 - normalized_value)
#             color_bar[i, :, :] = color

#         img_array = np.hstack((img_array, color_bar))

#     return img_array

# if __name__ == '__main__':
#     rows = 9#8
#     cols = 10#8
#     timer = Timer()
#     tactile_recorder = TactileSkin(serialPort="COM3", serialBaud=57600)
#     time.sleep(1.0)

#     # Specify the CSV file name
#     csv_filename = 'results1.csv'

#     print("Start streaming tactile data...")
#     start = time.time()

#     show_colorbar = True
#     text_display = False
#     displaying_image = False
#     image_start_time = None

#     # Determine the position for the "Guess" image
#     guess_window_x = 200
#     guess_window_y = 0

#     # Determine the position for the "Happy Halloween" image (adjust as needed)
#     halloween_window_x = guess_window_x
#     halloween_window_y = guess_image.shape[0]  # Position it below the "Guess" image
#     t1=0
#     for i in range(10000):
#         timestamp = timer.time
#         tactile_data = tactile_recorder.readData()
#         tactile_data = tactile_data[:-2].split(" ")[:-1]
#         #print(1/(time.time()-t1)) #time algo
#         t1 = time.time()
#         try:
#             tactile_data = np.array([int(item) for item in tactile_data])
#         except:
#             print("Data error!")
#             continue

#         if len(tactile_data) != rows * cols:
#             continue

#         # Write data to CSV file
#         write_to_csv(tactile_data, csv_filename)

#         tactile_img = heatMap(tactile_data * color_enhance, rows, cols, show_colorbar)
#         cv2.imshow('Tactile reading', tactile_img)

#         key = cv2.waitKey(1) & 0xFF
#         if key == ord('q'):
#             print("Quitting the data collection...")
#             break

#         # Toggle the colorbar display on 'c' key press
#         elif key == ord('c'):
#             show_colorbar = not show_colorbar

#         # Toggle the text display on 't' key press
#         elif key == ord('t'):
#             text_display = not text_display

#         elif key == ord('d'):
#             if not display_guess_image:
#                 cv2.namedWindow('Guess', cv2.WINDOW_NORMAL)
#                 cv2.moveWindow('Guess', guess_window_x, guess_window_y)
#                 cv2.imshow('Guess', guess_image)
#                 display_guess_image = True
#             else:
#                 cv2.destroyWindow('Guess')
#                 display_guess_image = False

#         # # Check if taxel units R1C1, R8C1, and R8C8 are pressed for more than 4 seconds
#         # if tactile_data[56] > activation_threshold and tactile_data[63] > activation_threshold:
#         #     if not displaying_image:
#         #         image_start_time = time.time()
#         #         displaying_image = True

#         #     # Load and display the "happy_halloween.png" image
#         #     if displaying_image:
#         #         image = cv2.imread("happy_halloween6.png")
#         #         cv2.namedWindow('Happy Halloween', cv2.WINDOW_NORMAL)
#         #         cv2.moveWindow('Happy Halloween', halloween_window_x, halloween_window_y+20)
#         #         cv2.imshow('Happy Halloween', image)

#         #     if displaying_image and (time.time() - image_start_time) > 4:
#         #         cv2.waitKey(4)  # Wait for 4 seconds
#         #         cv2.destroyWindow('Happy Halloween')
#         #         displaying_image = False

#     end = time.time()
#     print("Ended!", (end - start))

# cv2.destroyAllWindows()


# import os
# from datetime import datetime
# import numpy as np
# import time
# import cv2
# from timer import Timer
# from skin_sensor import TactileSkin

# text_display = False
# color_enhance = 1.5  #1.5
# activation_threshold = 150#150
# activation_threshold_game = 100
# # Flag to track if the "guess.png" image should be displayed
# display_guess_image = False
# guess_image = cv2.imread("guess.png")

# def heatMap(tactile_data, rows, cols, show_colorbar=True):
#     unit_w = 80
#     unit_h = 80
#     min_v = 0
#     max_v = 1024

#     def map_color(value):
#         if value < 0.25:
#             return (0, 0, int(255 * (value / 0.25)))
#         elif value < 0.5:
#             return (0, int(255 * ((value - 0.25) / 0.25)), 255)
#         elif value < 0.75:
#             return (int(255 * ((value - 0.5) / 0.25)), 255, 0)
#         else:
#             return (255, int(255 * (1 - (value - 0.75) / 0.25)), 0)

#     data_array = tactile_data.reshape((rows, cols))
#     img_array = np.zeros((unit_h * rows, unit_w * cols, 3), dtype=np.uint8)

#     for i in range(rows):
#         for j in range(cols):
#             normalized_value = (data_array[i, j] - min_v) / (max_v - min_v)
#             if data_array[i, j] < activation_threshold:  # Check the threshold
#                 color = (255, 0, 0)  # Set color to black if below the threshold
#             else:
#                 color = map_color(1 - normalized_value)
#             img_array[i * unit_h:(i + 1) * unit_h, j * unit_w:(j + 1) * unit_w, :] = color

#             if text_display:
#                 font = cv2.FONT_HERSHEY_SIMPLEX
#                 fontScale = 1
#                 text_color = (255, 255, 255)
#                 thickness = 2
#                 text = str(data_array[i, j])
#                 text_size = cv2.getTextSize(text, font, fontScale, thickness)[0]
#                 text_x = j * unit_w + (unit_w - text_size[0]) // 2
#                 text_y = i * unit_h + (unit_h + text_size[1]) // 2
#                 cv2.putText(img_array, text, (text_x, text_y), font, fontScale, text_color, thickness, cv2.LINE_AA)

#     if show_colorbar:
#         color_bar = np.zeros((unit_h * rows, 30, 3), dtype=np.uint8)
#         for i in range(unit_h * rows):
#             normalized_value = 1 - i / (unit_h * rows)
#             color = map_color(1 - normalized_value)
#             color_bar[i, :, :] = color

#         img_array = np.hstack((img_array, color_bar))

#     return img_array

# if __name__ == '__main__':
#     rows = 8
#     cols = 8
#     timer = Timer()
#     tactile_recorder = TactileSkin(serialPort="COM4", serialBaud=57600)
#     time.sleep(1.0)

#     print("Start streaming tactile data...")
#     start = time.time()

#     show_colorbar = True
#     text_display = False
#     displaying_image = False
#     image_start_time = None

#     # Determine the position for the "Guess" image
#     guess_window_x = 200
#     guess_window_y = 0

#     # Determine the position for the "Happy Halloween" image (adjust as needed)
#     halloween_window_x = guess_window_x
#     halloween_window_y = guess_image.shape[0]  # Position it below the "Guess" image

#     for i in range(10000):
#         timestamp = timer.time
#         tactile_data = tactile_recorder.readData()
#         tactile_data = tactile_data[:-2].split(" ")[:-1]

#         try:
#             tactile_data = np.array([int(item) for item in tactile_data])
#         except:
#             print("Data error!")
#             continue

#         if len(tactile_data) != rows * cols:
#             continue

#         tactile_img = heatMap(tactile_data * color_enhance, rows, cols, show_colorbar)
#         cv2.imshow('Tactile reading', tactile_img)

#         key = cv2.waitKey(1) & 0xFF
#         if key == ord('q'):
#             print("Quitting the data collection...")
#             break

#         # Toggle the colorbar display on 'c' key press
#         elif key == ord('c'):
#             show_colorbar = not show_colorbar

#         # Toggle the text display on 't' key press
#         elif key == ord('t'):
#             text_display = not text_display

#         elif key == ord('d'):
#             if not display_guess_image:
#                 cv2.namedWindow('Guess', cv2.WINDOW_NORMAL)
#                 cv2.moveWindow('Guess', guess_window_x, guess_window_y)
#                 cv2.imshow('Guess', guess_image)
#                 display_guess_image = True
#             else:
#                 cv2.destroyWindow('Guess')
#                 display_guess_image = False

#         # # Check if taxel units R1C1, R8C1, and R8C8 are pressed for more than 4 seconds
#         # if tactile_data[56] > activation_threshold_game and tactile_data[63] > activation_threshold_game:
#         #     if not displaying_image:
#         #         image_start_time = time.time()
#         #         displaying_image = True

#         #     # Load and display the "happy_halloween.png" image
#         #     if displaying_image:
#         #         image = cv2.imread("happy_halloween6.png")
#         #         cv2.namedWindow('Happy Halloween', cv2.WINDOW_NORMAL)
#         #         cv2.moveWindow('Happy Halloween', halloween_window_x, halloween_window_y + 20)
#         #         cv2.imshow('Happy Halloween', image)

#         #     if displaying_image and (time.time() - image_start_time) > 4:
#         #         cv2.waitKey(4)  # Wait for 4 seconds
#         #         cv2.destroyWindow('Happy Halloween')
#         #         displaying_image = False

#     end = time.time()
#     print("Ended!", (end - start))

# cv2.destroyAllWindows()


# import os
# from datetime import datetime
# import numpy as np
# import time
# import cv2
# from timer import Timer
# from skin_sensor import TactileSkin

# text_display = False
# color_enhance = 1.5
# activation_threshold = 100
# # Flag to track if the "guess.png" image should be displayed
# display_guess_image = False
# guess_image = cv2.imread("guess.png")

# def heatMap(tactile_data, rows, cols, show_colorbar=True):
#     unit_w = 80
#     unit_h = 80
#     min_v = 0
#     max_v = 1024

#     def map_color(value):
#         if value < 0.25:
#             return (0, 0, int(255 * (value / 0.25)))
#         elif value < 0.5:
#             return (0, int(255 * ((value - 0.25) / 0.25)), 255)
#         elif value < 0.75:
#             return (int(255 * ((value - 0.5) / 0.25)), 255, 0)
#         else:
#             return (255, int(255 * (1 - (value - 0.75) / 0.25)), 0)

#     data_array = tactile_data.reshape((rows, cols))
#     img_array = np.zeros((unit_h * rows, unit_w * cols, 3), dtype=np.uint8)

#     for i in range(rows):
#         for j in range(cols):
#             normalized_value = (data_array[i, j] - min_v) / (max_v - min_v)
#             color = map_color(1 - normalized_value)
#             img_array[i * unit_h:(i + 1) * unit_h, j * unit_w:(j + 1) * unit_w, :] = color

#             if text_display:
#                 font = cv2.FONT_HERSHEY_SIMPLEX
#                 fontScale = 1
#                 text_color = (255, 255, 255)
#                 thickness = 2
#                 text = str(data_array[i, j])
#                 text_size = cv2.getTextSize(text, font, fontScale, thickness)[0]
#                 text_x = j * unit_w + (unit_w - text_size[0]) // 2
#                 text_y = i * unit_h + (unit_h + text_size[1]) // 2
#                 cv2.putText(img_array, text, (text_x, text_y), font, fontScale, text_color, thickness, cv2.LINE_AA)

#     if show_colorbar:
#         color_bar = np.zeros((unit_h * rows, 30, 3), dtype=np.uint8)
#         for i in range(unit_h * rows):
#             normalized_value = 1 - i / (unit_h * rows)
#             color = map_color(1 - normalized_value)
#             color_bar[i, :, :] = color

#         img_array = np.hstack((img_array, color_bar))

#     return img_array

# if __name__ == '__main__':
#     rows = 8
#     cols = 8
#     timer = Timer()
#     tactile_recorder = TactileSkin(serialPort="COM6", serialBaud=57600)
#     time.sleep(1.0)

#     print("Start streaming tactile data...")
#     start = time.time()

#     show_colorbar = True
#     text_display = False
#     displaying_image = False
#     image_start_time = None

#     # Determine the position for the "Guess" image
#     guess_window_x = 200
#     guess_window_y = 0

#     # Determine the position for the "Happy Halloween" image (adjust as needed)
#     halloween_window_x = guess_window_x
#     halloween_window_y = guess_image.shape[0]  # Position it below the "Guess" image

#     for i in range(10000):
#         timestamp = timer.time
#         tactile_data = tactile_recorder.readData()
#         tactile_data = tactile_data[:-2].split(" ")[:-1]

#         try:
#             tactile_data = np.array([int(item) for item in tactile_data])
#         except:
#             print("Data error!")
#             continue

#         if len(tactile_data) != rows * cols:
#             continue

#         tactile_img = heatMap(tactile_data * color_enhance, rows, cols, show_colorbar)
#         cv2.imshow('Tactile reading', tactile_img)

#         key = cv2.waitKey(1) & 0xFF
#         if key == ord('q'):
#             print("Quitting the data collection...")
#             break

#         # Toggle the colorbar display on 'c' key press
#         elif key == ord('c'):
#             show_colorbar = not show_colorbar

#         # Toggle the text display on 't' key press
#         elif key == ord('t'):
#             text_display = not text_display

#         elif key == ord('d'):
#             if not display_guess_image:
#                 cv2.namedWindow('Guess', cv2.WINDOW_NORMAL)
#                 cv2.moveWindow('Guess', guess_window_x, guess_window_y)
#                 cv2.imshow('Guess', guess_image)
#                 display_guess_image = True
#             else:
#                 cv2.destroyWindow('Guess')
#                 display_guess_image = False

#         # Check if taxel units R1C1, R8C1, and R8C8 are pressed for more than 4 seconds
#         if tactile_data[56] > activation_threshold and tactile_data[63] > activation_threshold:
#             if not displaying_image:
#                 image_start_time = time.time()
#                 displaying_image = True

#             # Load and display the "happy_halloween.png" image
#             if displaying_image:
#                 image = cv2.imread("happy_halloween6.png")
#                 cv2.namedWindow('Happy Halloween', cv2.WINDOW_NORMAL)
#                 cv2.moveWindow('Happy Halloween', halloween_window_x, halloween_window_y+20)
#                 cv2.imshow('Happy Halloween', image)

#             if displaying_image and (time.time() - image_start_time) > 4:
#                 cv2.waitKey(4)  # Wait for 4 seconds
#                 cv2.destroyWindow('Happy Halloween')
#                 displaying_image = False

#     end = time.time()
#     print("Ended!", (end - start))

# cv2.destroyAllWindows()



# #original draft 

# import os
# from datetime import datetime
# import numpy as np
# import time
# import cv2
# from timer import Timer
# from skin_sensor import TactileSkin

# text_display = False
# color_enhance = 1.5

# def heatMap(tactile_data, rows, cols):
#     unit_w = 80
#     unit_h = 80
#     min_v = 0
#     max_v = 1024

#     def map_color(value):
#         # Map the value to a color gradient
#         if value < 0.25:
#             return (0, 0, int(255 * (value / 0.25)))  # Deep Blue to Blue-Green
#         elif value < 0.5:
#             return (0, int(255 * ((value - 0.25) / 0.25)), 255)  # Blue-Green to Yellow
#         elif value < 0.75:
#             return (int(255 * ((value - 0.5) / 0.25)), 255, 0)  # Yellow to Orange
#         else:
#             return (255, int(255 * (1 - (value - 0.75) / 0.25)), 0)  # Orange to Red

#     data_array = tactile_data.reshape((rows, cols))
#     img_array = np.zeros((unit_h * rows, unit_w * cols, 3), dtype=np.uint8)

#     for i in range(rows):
#         for j in range(cols):
#             normalized_value = (data_array[i, j] - min_v) / (max_v - min_v)
#             color = map_color(1-normalized_value)
#             img_array[i * unit_h:(i + 1) * unit_h, j * unit_w:(j + 1) * unit_w, :] = color

#             # Draw the tactile data value in the center of the grid unit

#             if text_display:
#                 font = cv2.FONT_HERSHEY_SIMPLEX
#                 fontScale = 1
#                 text_color = (255, 255, 255)  # White text
#                 thickness = 2
#                 text = str(data_array[i, j])
#                 text_size = cv2.getTextSize(text, font, fontScale, thickness)[0]
#                 text_x = j * unit_w + (unit_w - text_size[0]) // 2
#                 text_y = i * unit_h + (unit_h + text_size[1]) // 2
#                 cv2.putText(img_array, text, (text_x, text_y), font, fontScale, text_color, thickness, cv2.LINE_AA)

#     return img_array

# if __name__ == '__main__':
#     rows = 8
#     cols = 8
#     timer = Timer()
#     tactile_recorder = TactileSkin(serialPort="COM6", serialBaud=57600)
#     time.sleep(1.0)

#     print("Start streaming tactile data...")
#     start = time.time()

#     for i in range(10000):
#         timestamp = timer.time
#         tactile_data = tactile_recorder.readData()
#         tactile_data = tactile_data[:-2].split(" ")[:-1]

#         try:
#             tactile_data = np.array([int(item) for item in tactile_data])
#         except:
#             print("Data err!")
#             continue

#         if len(tactile_data) != rows * cols:
#             continue

#         tactile_img = heatMap(tactile_data, rows, cols)
#         cv2.imshow('Tactile reading', tactile_img)

#         key = cv2.waitKey(1) & 0xFF
#         if key == ord('q'):
#             print("Quitting the data collection...")
#             break

#     end = time.time()
#     print("Endd!", (end - start))

# cv2.destroyAllWindows()
