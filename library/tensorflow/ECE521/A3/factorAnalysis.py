import tensorflow as tf
import numpy as np
import sys
from dataInitializer import DataInitializer
from utils import * 
import datetime
import sys
import matplotlib.pyplot as plt

class FactorAnalysis(object):
    def __init__(self, questionTitle, K, trainData, trainTarget, validData, validTarget, testData, testTarget, dataType, numEpoch = 500, learningRate = 0.001): 
        """
        Constructor
        """
        self.K = K # number of factors
        self.trainData = trainData
        self.trainTarget = trainTarget
        self.validData = validData 
        self.validTarget = validTarget
        self.testData = testData
        self.testTarget = testTarget
        self.D = self.trainData[0].size # Dimension of each data
        print 'datadimension', self.D # TODO TEMP
        self.learningRate = learningRate
        self.numEpoch = numEpoch
        self.miniBatchSize = self.trainData.shape[0] # miniBatchSize is entire data size
        self.questionTitle = questionTitle
        self.optimizer = tf.train.AdamOptimizer(learning_rate = self.learningRate, beta1=0.9, beta2=0.99, epsilon=1e-5)
        # Execute Factor Analysis
        self.FactorAnalysisMethod()

    def saveGrayscaleImage(self, image, width=8, height=8, imageName=""):
        """ This plots an image given its width and height 
        image is the image to plot
        imageName is the name of the image to save as.
        """
        # Draw each figures (8, 8)
        currImage = image[:]
        currImage = np.reshape(currImage, (width,height))
        plt.imshow(currImage, interpolation="nearest", cmap="gray")
        plt.savefig(str(imageName) + ".png")

    def printTensor(self, tensorToPrint, trainData, message=""):
        init = tf.global_variables_initializer()
        sess = tf.InteractiveSession()
        sess.run(init)
        printDict = {trainData: self.trainData}
        valueToPrint = sess.run([tensorToPrint], feed_dict = printDict)
        print message, valueToPrint
        print "shape", np.array(valueToPrint).shape

    def printPlotResults(self, xAxis, yTrainErr, yValidErr, numUpdate, minAssignTrain, currTrainData, factorMean, factorStdDeviation, factorPrior,  minAssignValid):
        figureCount = 0 # TODO: Make global
        import matplotlib.pyplot as plt
        print "mean", factorMean
        print "K: ", self.K
        print "Iter: ", numUpdate
        numTrainAssignEachClass = np.bincount(minAssignTrain)
        numValidAssignEachClass = np.bincount(minAssignValid)
        print "Train Assignments To Classes:", numTrainAssignEachClass
        percentageTrainAssignEachClass = numTrainAssignEachClass/float(sum(numTrainAssignEachClass))
        print "Train Percentage Assignment To Classes:", percentageTrainAssignEachClass
        percentageValidAssignEachClass = percentageTrainAssignEachClass # Initialize
        print "Valid Assignments To Classes:", numValidAssignEachClass
        percentageValidAssignEachClass = numValidAssignEachClass/float(sum(numValidAssignEachClass))
        print "Valid Percentage Assignment To Classes:", percentageValidAssignEachClass
        print "prior", factorPrior
        print "prior.shape", factorPrior.shape
        print "prior Sum", np.sum(factorPrior)
        print "stdDeviation", factorStdDeviation
        print "stdDeviationShape", factorStdDeviation.shape
        print "Lowest TrainLoss", np.min(yTrainErr)
        print "Lowest ValidLoss", np.min(yValidErr)

        trainStr = "Train"
        validStr = "Valid"
        typeLossStr = "Loss"
        typeScatterStr = "Assignments"
        trainLossStr = trainStr + typeLossStr
        validLossStr = validStr + typeLossStr
        iterationStr = "Iteration"
        dimensionOneStr = "D1"
        dimensionTwoStr = "D2"
        paramStr = "K" + str(self.K) + "Learn" + str(self.learningRate) + "NumEpoch" + str(self.numEpoch)

        # Train Loss
        figureCount = figureCount + 1
        plt.figure(figureCount)
        title = trainStr + typeLossStr + paramStr
        plt.title(title)
        plt.xlabel(iterationStr)
        plt.ylabel(typeLossStr)
        plt.plot(np.array(xAxis), np.array(yTrainErr), label = trainLossStr)
        plt.legend()
        plt.savefig(self.questionTitle + title + ".png")
        plt.close()
        plt.clf()

        # Valid Loss
        figureCount = figureCount + 1
        plt.figure(figureCount)
        title = validStr + typeLossStr + paramStr
        plt.title(title)
        plt.xlabel(iterationStr)
        plt.ylabel(typeLossStr)
        plt.plot(np.array(xAxis), np.array(yValidErr), label = validLossStr)
        plt.legend()
        plt.savefig(self.questionTitle + title + ".png")
        plt.close()
        plt.clf()

        if self.dataType != "2D":
            return
        # Plot percentage in each different classes as well
        # Scatter plot based on assignment colors
        # Including percentage as the label
        # Train Scatter Plot
        figureCount = figureCount + 1
        plt.figure(figureCount)
        plt.axes()
        title = trainStr + typeScatterStr + paramStr
        plt.title(title)
        plt.xlabel(dimensionOneStr)
        plt.ylabel(dimensionTwoStr)
        colors = ['blue', 'red', 'green', 'black', 'yellow']
        plt.scatter(currTrainData[:, 0], currTrainData[:, 1], c=minAssignTrain, s=10, alpha=0.5)
        colors = colors[:self.K]
        for i, j, k, l in zip(factorMean, percentageTrainAssignEachClass, colors, factorStdDeviation[0]):
            plt.plot(i[0], i[1], 'kx', markersize=15, label=j, c=k)
            circle = plt.Circle((i[0], i[1]), radius=2*l, color=k, fill=False)
            plt.gca().add_patch(circle)
        plt.legend()
        plt.savefig(self.questionTitle + title + ".png")
        plt.close()
        plt.clf()

        # Valid Scatter Plot
        figureCount = figureCount + 1
        plt.figure(figureCount)
        plt.axes()
        title = validStr + typeScatterStr + paramStr
        plt.title(title)
        plt.xlabel(dimensionOneStr)
        plt.ylabel(dimensionTwoStr)
        colors = ['blue', 'red', 'green', 'black', 'yellow']
        plt.scatter(self.validData[:, 0], self.validData[:, 1], c=minAssignValid, s=10, alpha=0.5)
        colors = colors[:self.K]
        for i, j, k, l in zip(factorMean, percentageValidAssignEachClass, colors, factorStdDeviation[0]):
            plt.plot(i[0], i[1], 'kx', markersize=15, label=j, c=k)
            circle = plt.Circle((i[0], i[1]), radius=2*l, color=k, fill=False)
            plt.gca().add_patch(circle)
        plt.legend()
        plt.savefig(self.questionTitle + title + ".png")
        plt.close()
        plt.clf()

    def PairwiseDistances(self, X, U):
        """
        input:
            X is a matrix of size (B x D)
            U is a matrix of size (K x D)
        output:
            Distances = matrix of size (B x K) containing the pairwise Euclidean distances
        """
        batchSize = tf.shape(X)[0] 
        dimensionSize = tf.shape(X)[1]
        numClusters = tf.shape(U)[0]
        X_broadcast = tf.reshape(X, (batchSize, 1, dimensionSize))
        sumOfSquareDistances = tf.reduce_sum(tf.square(tf.subtract(X_broadcast, U)), 2)
        return sumOfSquareDistances

    def LnProbabilityXGivenZ(self, data, mean, variance):
        sumOfSquare = self.PairwiseDistances(data, mean)
        logLikelihoodDataGivenCluster = tf.add(-tf.multiply(tf.cast(self.D, tf.float32)/2.0,tf.log(tf.constant(2.0*np.pi)*variance)), -tf.divide(sumOfSquare, 2.0*variance))
        return logLikelihoodDataGivenCluster

    def LnProbabilityZGivenX(self, data, mean, variance, lnPriorBroad):
        lnProbabilityXGivenZ = self.LnProbabilityXGivenZ(data, mean, variance)
        # lnPriorBroad = tf.log(tf.reshape(prior, (1, self.K)))
        numerator = lnPriorBroad + lnProbabilityXGivenZ
        lnProbabilityX = tf.reshape(reduce_logsumexp(numerator, 1), (tf.shape(data)[0], 1))
        lnProbabilityZGivenX = numerator - lnProbabilityX
        return lnProbabilityZGivenX
        # Monotonically increasing, others doesnt matter ??
        # return numerator

    def LnProbabilityX(self, data, mean, variance, lnPriorBroad):
        lnProbabilityXGivenZ = self.LnProbabilityXGivenZ(data, mean, variance)
        # lnPriorBroad = tf.log(tf.reshape(prior, (1, self.K)))
        numerator = lnPriorBroad + lnProbabilityXGivenZ
        lnProbabilityX = tf.reshape(reduce_logsumexp(numerator, 1), (tf.shape(data)[0], 1))
        return lnProbabilityX


    def FactorAnalysisMethod(self):
        ''' 
        Build Graph and execute in here
        so don't have to pass variables one by one
        Bad Coding Style but higher programmer productivity
        '''
        # Build Graph 
        print "trainShape", self.trainData.shape
        print "validShape", self.validData.shape
        print "testShape", self.testData.shape
        self.saveGrayscaleImage(self.trainData[0], 8, 8, "temp0")
        factorMean = tf.Variable(tf.truncated_normal([self.D]))
        factorWeights = tf.Variable(tf.truncated_normal([self.D, self.K]))
        factorStdDeviationConstraint = tf.Variable(tf.truncated_normal([self.D]))
        factorTraceCoVariance = tf.exp(factorStdDeviationConstraint)
        factorCovariance = tf.diag(factorStdDeviationConstraint)
        trainData = tf.placeholder(tf.float32, shape=[None, self.D], name="trainingData")

        sumOfSquare = self.PairwiseDistances(trainData, factorMean)

        # Determinant of covariance matrix
        # log_det = 2.0 * tf.reduce_sum(tf.log(tf.diag_part(tf.cholesky(A))))

        self.printTensor(sumOfSquare, trainData, "trainData")
        sys.exit(0)

        lnProbabilityXGivenZ = self.LnProbabilityXGivenZ(trainData, factorMean, factorVariance)
        #lnProbabilityX = self.LnProbabilityX(trainData, factorMean, factorStdDeviation, factorPrior)
        lnProbabilityX = self.LnProbabilityX(trainData, factorMean, factorVariance, logClusterConstraint)
        #loss = tf.negative(tf.reduce_sum(lnProbabilityX))
        loss = (tf.reduce_sum(-1.0 * lnProbabilityX))
        # This is needed to decide which assignment it is
        #lnProbabilityZGivenX = self.LnProbabilityZGivenX(trainData, factorMean, factorStdDeviation, factorPrior)
        lnProbabilityZGivenX = self.LnProbabilityZGivenX(trainData, factorMean, factorVariance, logClusterConstraint)
        probabilityZGivenX = tf.exp(lnProbabilityZGivenX)
        check = tf.reduce_sum(probabilityZGivenX, 1) # Check probabilities sum to 1
        # Assign classes based on maximum posterior probability for each data point
        minAssignments = tf.argmax(lnProbabilityXGivenZ, 1) # No prior contribution during assignment
        minAssignments = tf.argmax(lnProbabilityZGivenX, 1) # Prior contributes during assignment

        # ----------------------------------------------------------------------------------
        #logLikelihoodDataGivenCluster = self.LnProbabilityZGivenX(trainData, factorMean, factorStdDeviation, factorPrior)
        validLoss = loss # initialization
        minValidAssignments = minAssignments #Initialization
        valid_data = tf.placeholder(tf.float32, shape=[None, self.D], name="validationData")
        validLoss = tf.reduce_sum(-1.0 * self.LnProbabilityX(valid_data, factorMean,factorVariance,logClusterConstraint))
        validLnProbabilityZGivenX = self.LnProbabilityZGivenX(valid_data, factorMean, factorVariance, logClusterConstraint)
        minValidAssignments = tf.argmax(validLnProbabilityZGivenX, 1) # Prior contributes during assignment

        train = self.optimizer.minimize(loss)
        
        # Session
        init = tf.global_variables_initializer()
        sess = tf.InteractiveSession()
        sess.run(init)
        currEpoch = 0
        minAssignTrain = 0
        minAssignValid = 0
        centers = 0
        xAxis = []
        yTrainErr = []
        yValidErr = []
        numUpdate = 0
        step = 0
        currTrainDataShuffle = self.trainData
        while currEpoch < self.numEpoch:
            np.random.shuffle(self.trainData) # Shuffle Batches
            step = 0
            while step*self.miniBatchSize < self.trainData.shape[0]:
                feedDicts = {trainData: self.trainData[step*self.miniBatchSize:(step+1)*self.miniBatchSize], valid_data: self.validData}
                _, minAssignTrain, paramClusterMean, paramClusterPrior, paramClusterStdDeviation, zGivenX, checkZGivenX, errTrain, errValid, minAssignValid = sess.run([train, minAssignments, factorMean, factorPrior, factorStdDeviation, lnProbabilityZGivenX, check, loss, validLoss, minValidAssignments], feed_dict = feedDicts)
                xAxis.append(numUpdate)
                yTrainErr.append(errTrain)
                yValidErr.append(errValid)
                step += 1
                numUpdate += 1
            currEpoch += 1

            if currEpoch%100 == 0:
                logStdOut("e: " + str(currEpoch))
        # Calculate everything again without training
        feedDicts = {trainData: self.trainData}
        # No training, just gather data for valid assignments 
        feedDicts = {trainData: self.trainData, valid_data: self.validData}
        minAssignTrain, paramClusterMean, paramClusterPrior, paramClusterStdDeviation, zGivenX, checkZGivenX, errTrain, errValid, minAssignValid = sess.run([minAssignments, factorMean, factorPrior, factorStdDeviation, lnProbabilityZGivenX, check, loss, validLoss, minValidAssignments], feed_dict = feedDicts)
        # Count how many assigned to each class
        currTrainDataShuffle = self.trainData
        # TODO: Uncomment once ready
        # self.printPlotResults(xAxis, yTrainErr, yValidErr, numUpdate, minAssignTrain, currTrainDataShuffle, paramClusterMean, paramClusterStdDeviation, paramClusterPrior, minAssignValid)

def executeFactorAnalysis(questionTitle, K, numEpoch, learningRate):
    """
    Re-loads the data and re-randomize it with same seed anytime to ensure replicable results
    """
    logStdOut(questionTitle)
    print questionTitle
    trainData = 0
    validData = 0
    # Load data with seeded randomization
    dataInitializer = DataInitializer()
    trainData, trainTarget, validData, validTarget, testData, testTarget = dataInitializer.getTinyData()

    # Execute algorithm 
    kObject = FactorAnalysis(questionTitle, K, trainData, trainTarget, validData, validTarget, testData, testTarget, numEpoch, learningRate)
    logElapsedTime(questionTitle + "K" + str(K) + "NumEpoch" + str(numEpoch))

# Global for logging
questionTitle = "" # Need to be global for logging to work
startTime = datetime.datetime.now()
figureCount = 1 # To not overwrite existing pictures

def logStdOut(message):
    # Temporary print to std out
    # sys.stdout = sys.__stdout__ # TODO: Uncomment this
    print message
    # Continue editing same file
    # sys.stdout = open("result" + questionTitle + ".txt", "a") #TODO: Uncomment this

def logElapsedTime(message):
    ''' Logs the elapsedTime with a given message '''
    global startTime 
    endTime = datetime.datetime.now()
    elapsedTime = endTime - startTime
    hours, remainder = divmod(elapsedTime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    totalDays = elapsedTime.days
    timeStr = str(message) + ': Days: ' + str(totalDays) +  " hours: " + str(hours) + ' minutes: ' + str(minutes) +  ' seconds: ' + str(seconds)
    logStdOut(timeStr)
    startTime = datetime.datetime.now()

if __name__ == "__main__":
    print "ECE521 Assignment 3: Unsupervised Learning: Factor Analysis"
    questionTitle = "3.1.2"
    numEpoch = 200
    learningRate = 0.1
    K = 4
    executeFactorAnalysis(questionTitle, K, numEpoch, learningRate)
    # '''
    
    '''
    questionTitle = "3.1.3"
    diffK = [1, 2, 3, 4, 5]
    # for K in diffK:
        executeFactorAnalysis(questionTitle, K, dataType, numEpoch, learningRate)
    # TODO:
    # '''

