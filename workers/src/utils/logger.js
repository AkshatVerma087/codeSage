function log(level, message, meta = {}){
    const entry = {
        timestamp: new Date().toISOString(),
        service: 'worker',
        level,
        jobId: meta.jobId || null,
        correlationId: meta.correlationId || null,
        ...meta,
    };

    console.log(JSON.stringify(entry));
}

module.exports = {
    info: (message, meta) => log('info', message, meta),
    error: (message, meta) => log('error', message, meta),
    warn: (message, meta) => log('warn', message, meta),
};