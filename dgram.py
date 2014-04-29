from PIL import Image, ImageDraw

def getheight(clust):
    # Is this an endpoint? Then the height is just 1
    if clust.left == None and clust.right == None:
        return 1

    # Otherwise the height is the same of the heights of
    # each bramnch
    result = getheight(clust.left) + getheight(clust.right)
    print result
    return result

def getdepth(clust):
    # The distance of an endpoint is 0.0
    if clust.left == None and clust.right == None:
        return 0

    # The distance of a branch is the graeter of its two sides
    # plus its own distance
    return max(getdepth(clust.left), getdepth(clust.right))+clust.distance

def drawdendrogram(clust, labels, jpeg = 'clusters.jpg'):
    # height and width
    h = getheight(clust) * 20
    w = 1200
    depth = getdepth(clust)

    # width is fixed, so scale distances accoringly
    scaling = float(w-300)/depth

    # Create a new image with a white background
    img = Image.new('RGB', (w,h), (255,255,255))
    draw = ImageDraw.Draw(img)

    draw.line((0, h/2, 10, h/2), fill = (255, 0, 0))

    # Draw the first node
    drawnode(draw, clust, 10, (h/2), scaling, labels)
    img.save(jpeg, 'JPEG')

def drawnode(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        print 'node',clust.id
        h1 = getheight(clust.left) * 20
        h2 = getheight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2
        # Line length
        ll = clust.distance * scaling
        # Vertical line from this cluster to children
        draw.line((x, top + h1/2, x, bottom - h2/2), fill = (255, 0, 0))
        
        # Horizontal line to left item
        draw.line((x, top + h1/2, x + ll, top + h1/2), fill = (255, 0, 0))

        # Horizontal line to right item
        draw.line((x, bottom - h2/2, x + ll, bottom - h2/2), fill = (255, 0, 0))
        drawnode(draw, clust.left, x+ll, top+h1/2, scaling, labels)
        drawnode(draw, clust.right, x+ll, bottom-h2/2, scaling, labels)
    else:
        # If this is an endpoint, draw the item label
        print labels[clust.id]
        draw.text((x+5, y-7), labels[clust.id], (0,0,0))


