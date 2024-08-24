class ETLTasks:
    async def pipeline(self):
        self.extract()
        self.transform()
        self.load()

    async def launches(self):
        pass

    async def missions(self):
        pass

    async def rockets(self):
        pass
