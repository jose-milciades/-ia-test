import logging


class Log(object):

	@staticmethod
	def i(clazz, message):
		logger = logging.getLogger(clazz)
		logger.info(message)

	@staticmethod
	def e(clazz, message):
		logger = logging.getLogger(clazz)
		logger.error(message)

	@staticmethod
	def x(clazz, message):
		logger = logging.getLogger(clazz)
		logger.exception(message)
