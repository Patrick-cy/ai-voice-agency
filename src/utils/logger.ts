

function formatPrefix(level: string) {
	return `[${level}] ${new Date().toISOString()}`;
}

export function info(...args: any[]) {
	console.log(formatPrefix('INFO'), ...args);
}

export function warn(...args: any[]) {
	console.warn(formatPrefix('WARN'), ...args);
}

export function error(...args: any[]) {
	console.error(formatPrefix('ERROR'), ...args);
}

export function debug(...args: any[]) {
	
	if (process.env.DEBUG?.toLowerCase() === 'true') {
		console.debug(formatPrefix('DEBUG'), ...args);
	}
}

