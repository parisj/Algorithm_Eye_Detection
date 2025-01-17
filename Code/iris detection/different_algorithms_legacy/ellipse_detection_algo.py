import cv2
import numpy as np
import matplotlib.pyplot as plt
import create_plots as cp
import math 

def findEllipses(edges):
    # Create empty masks
    ellipseMask = np.zeros(edges.shape, dtype=np.uint8)
    contourMask = np.zeros(edges.shape, dtype=np.uint8)
    pi_4 = np.pi * 4
    ellipse_info = None
    
    # Find contours in preprocessed roi
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    # iterate over all contours found
    for contour in contours:

        # filter out too short
        if len(contour) < 20:
            continue

        area = cv2.contourArea(contour)
        
        # filter out too small
        if area <= 500:  
            continue

        arclen = cv2.arcLength(contour, True)
        
        # Kullback–Leibler divergence
        circularity = (pi_4 * area) / (arclen * arclen)
        
        ellipse = cv2.fitEllipse(contour)
        poly = cv2.ellipse2Poly((int(ellipse[0][0]), int(ellipse[0][1])), (int(ellipse[1][0] / 2), int(ellipse[1][1] / 2)), int(ellipse[2]), 0, 360, 5)

        # if contour is circular enough
        if circularity > 0.6:
            cv2.fillPoly(ellipseMask, [poly], 255)
            ellipse_info = ellipse
            continue

        # if contour has enough similarity to an ellipse
        similarity = cv2.matchShapes(poly.reshape((poly.shape[0], 1, poly.shape[1])), contour, 2, 0)
        if similarity <= 0.5:
            cv2.fillPoly(contourMask, [poly], 255)

    return ellipseMask, contourMask, ellipse_info


    
def best_ellipse(roi):
    # Convert the roi to grayscale if it's not already
    #print('Start calc Roi')
   
    #cv2.waitKey(0)
    # Get the contours of the ROI
    contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    plot_contours(roi, contours)
    # Find the contour with the largest area
    max_similarity = 10
    max_circularity = 0
    max_contour = None
    best_ellipse = None
    max_area = 0
    
    for contour in contours:
        
        #canvis = np.zeros_like(roi)
        #cv2.drawContours(canvis, contour, -1,(255,255,255),-1)
        #cv2.imshow('canvis', canvis)

        BOOL_ELLIPSE, contourMask, ellipse, similarity, circularity = is_contour_ellipse(roi, contour,max_area)
        if BOOL_ELLIPSE: 
            if max_similarity > similarity and max_circularity < circularity:
                max_contour = contourMask
                best_ellipse = ellipse
                cv2.imshow('contourMask', contourMask)


        # Check if max_contour is None, and return appropriate values
    if max_contour is None:
        print('None found ')
        return None
    


    return  best_ellipse


def plot_contours(image, contours):
    # Create a copy of the image
    image_copy = image.copy()

    # Draw all contours on the image
    cv2.drawContours(image_copy, contours, -1, (0, 255, 0), 2)

    # Convert BGR image to RGB for Matplotlib
    image_rgb = cv2.cvtColor(image_copy, cv2.COLOR_BGR2RGB)

    # Create a figure and axes
    fig, ax = plt.subplots()

    # Display the image
    ax.imshow(image_rgb)

    # Set axis ticks to empty
    ax.set_xticks([])
    ax.set_yticks([])

    # Show the plot
    plt.show()

def is_contour_ellipse(gray_roi, contour, max_area):
    
    
    contourMask = np.zeros(gray_roi.shape, dtype=np.uint8)
    if len(contour) < 20:  # A minimum of 5 points is required to fit an ellipse
        return False, contourMask, None, 10, 10
    
    ellipse = cv2.fitEllipse(contour)
    poly = cv2.ellipse2Poly((round(ellipse[0][0]), round(ellipse[0][1])), (round(ellipse[1][0] / 2), round(ellipse[1][1] / 2)), round(ellipse[2]), 0, 360, 1)
    similarity = cv2.matchShapes(poly.reshape((poly.shape[0], 1, poly.shape[1])), contour, 2, 0)

    area = cv2.contourArea(contour)
     
     # filter out too small
    if area <= 1000:  
        return False,None, None,10, 10
    arclen = cv2.arcLength(contour, True)
     
     # Kullback–Leibler divergence
    circularity = (4*np.pi * area) / (arclen * arclen)
    #print('similarity',similarity, 'circularity', circularity)
    
    if similarity <= 0.8 and circularity >= 0.2 and max_area < area :
        cv2.fillPoly(contourMask, [poly], 255)
        #cv2.imshow('contourMaks accepted', contourMask)
        #cv2.waitKey(0)
        return True, contourMask,ellipse, similarity, circularity
    

    
    #cv2.ellipse(img_gray, ellipse, (255,255,255), 1)
    #cv2.imshow('img_gray not accepted', img_gray)
  
   
    return  False,contourMask,None, 10, 10

if __name__ == '__main__':
    test = cv2.imread('Latex/thesis/plots/results/roi_text_resutls.png')
    final = test.copy()
    test = cv2.cvtColor(test, cv2.COLOR_BGR2GRAY) 
    cv2.imshow('test', test)
    test = cv2.GaussianBlur(test, (21,21),0)

    ret, roi_thresh = cv2.threshold(test, 60, 255, cv2.THRESH_BINARY_INV)
    cv2.imwrite('Latex/thesis/plots/results/roi_binary_ellipse.png', roi_thresh)

    cv2.imshow('roi_thresh', roi_thresh)
    ellipse = best_ellipse(roi_thresh)
    test = cv2.cvtColor(test, cv2.COLOR_GRAY2BGR) 

    cv2.ellipse(final, ellipse, (0,0,255), 1)
    cv2.imshow('test_1', final)
    cv2.imwrite('Latex/thesis/plots/results/roi_result_binary_ellipse.png', final)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
