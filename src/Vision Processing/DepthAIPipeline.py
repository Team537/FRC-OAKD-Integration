import depthai as dai

class DepthAIPipeline:
    def __init__(self):
        self.pipeline = None
        self.device = None
        self.video_queue = None
        self.depth_queue = None

    def create_pipeline(self):
        """
        Creates and returns a DepthAI pipeline that streams both RGB and Depth frames.
        
        Returns:
            pipeline (dai.Pipeline): The DepthAI pipeline
        """
        pipeline = dai.Pipeline()

        # Create camera nodes.
        camera = pipeline.createColorCamera()
        camera.setResolution(dai.ColorCameraProperties.SensorResolution.THE_720_P)
        camera.setInterleaved(False)
        camera.setFps(35)
        camera.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)

        # Enable undistortion
        camera.setCameraConfig(dai.CameraConfig.ISP, enableUndistortion=True)

        # Create Mono cameras for depth calculation
        left = pipeline.createMonoCamera()
        right = pipeline.createMonoCamera()
        left.setBoardSocket(dai.CameraBoardSocket.LEFT)
        right.setBoardSocket(dai.CameraBoardSocket.RIGHT)

        # Create depth node
        depth = pipeline.createStereoDepth()
        left.out.link(depth.left)
        right.out.link(depth.right)

        # Configure Depth Node Settings
        depth.setOutputRectified(True)
        depth.setLeftRightCheck(True)
        depth.setExtendedDisparity(True)
        depth.setSubpixel(True)
        depth.setResolution(dai.StereoDepthProperties.SensorResolution.THE_720P)

        # Create XLink output for video and depth streams
        xout_video = pipeline.createXLinkOut()
        xout_video.setStreamName("video")
        camera.preview.link(xout_video.input)

        xout_depth = pipeline.createXLinkOut()
        xout_depth.setStreamName("depth")
        depth.depth.link(xout_depth.input)

        # Return the newly created pipeline
        return pipeline

    def start_pipeline(self):
        """
        Starts the DepthAI pipeline.
        """
        print("Starting DepthAI Pipeline")

        # Set the pipeline and start the device
        self.pipeline = self.create_pipeline()
        self.device = dai.Device(self.pipeline)
        self.device.startPipeline()

        # Get the output queues for video and depth streams
        self.video_queue = self.device.getOutputQueue(name="video", maxSize=4, blocking=False)
        self.depth_queue = self.device.getOutputQueue(name="depth", maxSize=4, blocking=False)

    def stop_pipeline(self):
        """
        Stops the pipeline and cleans up.
        """
        self.device = None

    def get_color_camera_intrinsics(self):
        """
        Returns the color camera's intrinsic camera matrix.
        """
        return self.device.readCalibration().getCameraIntrinsics()

    def get_frame(self):
        """
        Returns the most recent RGB frame captured by the color camera.
        """
        return self.video_queue.get().getCvFrame()

    def get_depth_frame(self):
        """
        Returns the most recent depth frame captured by the depth camera.
        """
        return self.depth_queue.get().getCvFrame()