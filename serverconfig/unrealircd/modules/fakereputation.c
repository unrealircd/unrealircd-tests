/* Fake reputation
 * DO NOT USE THIS ON A LIVE SERVER. IT IS FOR THE TESTING SUITE *ONLY*.
 * If you use it on a server accessible by other users then they can
 * set any reputation value they choose which has a major negative
 * impact on security. Also, this module only works well the first few
 * minutes after booting, along with some other caveats. AGAIN,
 * IT IS ONLY FOR THE TEST SUITE!!
 *
 * (C) Copyright 2020 Bram Matthys and The UnrealIRCd Team
 * License: GPLv2
 */

#include "unrealircd.h"

CMD_FUNC(cmd_fakereputation);

ModuleHeader MOD_HEADER
  = {
	"third/fakereputation",
	"5.0",
	"/FAKEREPUTATION command for testing",
	"UnrealIRCd Team",
	"unrealircd-5",
    };

MOD_INIT()
{
	CommandAdd(modinfo->handle, "FAKEREPUTATION", cmd_fakereputation, 1, CMD_USER);
	ISupportAdd(modinfo->handle, "FAKEREPUTATION", NULL);
	MARK_AS_OFFICIAL_MODULE(modinfo);
	return MOD_SUCCESS;
}

MOD_LOAD()
{
	return MOD_SUCCESS;
}

MOD_UNLOAD()
{
	return MOD_SUCCESS;
}

CMD_FUNC(cmd_fakereputation)
{
	int v;
	char buf[64];

	if ((parc < 2) || BadPtr(parv[1]) || (atoi(parv[1]) < 1))
	{
		sendnotice(client, "Syntax is: /FAKEREPUTATION <value>");
		sendnotice(client, "  Example: /FAKEREPUTATION 5");
		return;
	}

	v = atoi(parv[1]);
	if (v > 10000)
	{
		sendnotice(client, "ERROR: Requested reputation value out of range, max is 10000");
		return;
	}
	/* And make it a number again. Yes we do it this way so nobody sets '1ab' or something */
	snprintf(buf, sizeof(buf), "%d", v);
	moddata_client_set(client, "reputation", buf);
	broadcast_md_client_cmd(NULL, &me, client, "reputation", buf);
	sendnotice(client, "Reputation set to %s", buf);
}
