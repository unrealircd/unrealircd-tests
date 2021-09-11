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
#if UNREAL_VERSION < 0x05000000
	"unrealircd-5",
#else
	"unrealircd-6",
#endif
    };

MOD_INIT()
{
	CommandAdd(modinfo->handle, "FAKEREPUTATION", cmd_fakereputation, MAXPARA, CMD_USER);
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
		sendnotice(client, "Syntax 1 is: /FAKEREPUTATION <value>");
		sendnotice(client, "  Example 1: /FAKEREPUTATION 5");
		sendnotice(client, "Syntax 2 is: /FAKEREPUTATION <ip> <value>");
		sendnotice(client, "  Example 2: /FAKEREPUTATION 127.0.0.1 5");
		return;
	}

	if ((strchr(parv[1], '.') || strchr(parv[1], ':')) && !BadPtr(parv[2]))
	{
		/* FAKEREPUTATION <ip> <value> */
		const char *parx[4];
		parx[0] = NULL;
		parx[1] = parv[1];
		parx[2] = parv[2];
		parx[3] = NULL;
		sendnotice(client, "Reputation for '%s' set to '%s'", parv[1], parv[2]);
		do_cmd(&me, NULL, "REPUTATION", 3, parx);
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
