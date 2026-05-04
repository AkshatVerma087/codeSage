const { randomUUID } = require('crypto');

function correlationMiddleware(req, res, next) {
    const headerValue = req.headers['x-correlation-id'];
    const provided = typeof headerValue === 'string' && headerValue.trim() ? headerValue.trim() : null;

    req.correlationId = provided || randomUUID();
    res.setHeader('x-correlation-id', req.correlationId);

    next();
}

module.exports = {
    correlationMiddleware,
};
