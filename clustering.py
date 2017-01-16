from sklearn import datasets
from sklearn import cluster
import matplotlib.pyplot as plt
import numpy as np
from skimage import io
import os
import psycopg2
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

#k = 10
#kmeans = cluster.KMeans(n_clusters=k)
#kmeans.fit(data)

images = []
base_dir = "/Users/theostyles/PycharmProjects/extractLetters/page-0884"
os.chdir(base_dir)


# Connect to DB
conn = psycopg2.connect("dbname=fyp user=theostyles")
cur = conn.cursor()
cur.execute("SELECT z00, z01, z02, z10, z11, z12, z20, z21, z22 FROM moments WHERE page = 884 AND y BETWEEN 500 AND 5500 ORDER BY y ASC;")
results_870 = cur.fetchall()

final_results = []
for result in results_870:
    final_results.append(list(result))

final_results = np.array(final_results)
#final_results = scale(final_results)
k = 10
reduced_data = PCA(n_components=2).fit_transform(final_results)
kmeans = cluster.KMeans(n_clusters=k).fit(reduced_data)

# Step size of the mesh. Decrease to increase the quality of the VQ.
h = .02     # point in the mesh [x_min, x_max]x[y_min, y_max].

# Plot the decision boundary. For that, we will assign a color to each
x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

# Obtain labels for each point in mesh. Use last trained model.
Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

# Put the result into a color plot
Z = Z.reshape(xx.shape)
plt.figure(1)
plt.clf()
plt.imshow(Z, interpolation='nearest',
           extent=(xx.min(), xx.max(), yy.min(), yy.max()),
           cmap=plt.cm.Paired,
           aspect='auto', origin='lower')

plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
# Plot the centroids as a white X
centroids = kmeans.cluster_centers_
plt.scatter(centroids[:, 0], centroids[:, 1],
            marker='x', s=169, linewidths=3,
            color='w', zorder=10)
plt.title('K-means clustering on the digits dataset (PCA-reduced data)\n'
          'Centroids are marked with white cross')
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.xticks(())
plt.yticks(())
plt.show()