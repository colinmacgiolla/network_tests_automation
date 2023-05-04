"""
BGP test functions
"""
import logging
from typing import Any, Dict, Optional, cast

from anta.decorators import check_bgp_family_enable
from anta.models import AntaTest, AntaTestCommand, AntaTestTemplate

logger = logging.getLogger(__name__)


def _check_bgp_vrfs(bgp_vrfs: Dict[str, Any]) -> Dict[str, Any]:
    """
    TODO
    """
    state_issue: Dict[str, Any] = {}
    for vrf in bgp_vrfs:
        for peer in bgp_vrfs[vrf]["peers"]:
            if (
                (bgp_vrfs[vrf]["peers"][peer]["peerState"] != "Established")
                or (bgp_vrfs[vrf]["peers"][peer]["inMsgQueue"] != 0)
                or (bgp_vrfs[vrf]["peers"][peer]["outMsgQueue"] != 0)
            ):
                vrf_dict = state_issue.setdefault(vrf, {})
                vrf_dict.update(
                    {
                        peer: {
                            "peerState": bgp_vrfs[vrf]["peers"][peer]["peerState"],
                            "inMsgQueue": bgp_vrfs[vrf]["peers"][peer]["inMsgQueue"],
                            "outMsgQueue": bgp_vrfs[vrf]["peers"][peer]["outMsgQueue"],
                        }
                    }
                )

    return state_issue


class VerifyBGPIPv4UnicastState(AntaTest):
    """
    Verifies all IPv4 unicast BGP sessions are established (for all VRF)
    and all BGP messages queues for these sessions are empty (for all VRF).

    * self.result = "skipped" if no BGP vrf are returned by the device
    * self.result = "success" if all IPv4 unicast BGP sessions are established (for all VRF)
                         and all BGP messages queues for these sessions are empty (for all VRF).
    * self.result = "failure" otherwise.
    """

    name = "VerifyBGPIPv4UnicastState"
    description = "Verifies all IPv4 unicast BGP sessions are established (for all VRF) and all BGP messages queues for these sessions are empty (for all VRF)."
    categories = ["routing", "bgp"]
    commands = [AntaTestCommand(command="show bgp ipv4 unicast summary vrf all")]

    @check_bgp_family_enable("ipv4")
    @AntaTest.anta_test
    def test(self) -> None:
        """Run VerifyBGPIPv4UnicastState validation"""

        command_output = cast(Dict[str, Dict[Any, Any]], self.instance_commands[0].output)
        state_issue = _check_bgp_vrfs(command_output["vrfs"])

        if not state_issue:
            self.result.is_success()
        else:
            self.result.is_failure(f"Some IPv4 Unicast BGP Peer are not up: {state_issue}")


class VerifyBGPIPv4UnicastCount(AntaTest):
    """
    Verifies all IPv4 unicast BGP sessions are established
    and all BGP messages queues for these sessions are empty
    and the actual number of BGP IPv4 unicast neighbors is the one we expect.

    * self.result = "skipped" if the `number` or `vrf` parameter is missing
    * self.result = "success" if all IPv4 unicast BGP sessions are established
                         and if all BGP messages queues for these sessions are empty
                         and if the actual number of BGP IPv4 unicast neighbors is equal to `number.
    * self.result = "failure" otherwise.
    """

    name = "VerifyBGPIPv4UnicastCount"
    description = (
        "Verifies all IPv4 unicast BGP sessions are established and all their BGP messages queues are empty and "
        " the actual number of BGP IPv4 unicast neighbors is the one we expect."
    )
    categories = ["routing", "bgp"]
    template = AntaTestTemplate(template="show bgp ipv4 unicast summary vrf {vrf}")

    @check_bgp_family_enable("ipv4")
    @AntaTest.anta_test
    def test(self, number: Optional[int] = None) -> None:
        """Run VerifyBGPIPv4UnicastCount validation"""

        if not number:
            self.result.is_skipped("VerifyBGPIPv4UnicastCount could not run because number was not supplied")
            return
        vrf = self.template_params[0]["vrf"]
        command_output = cast(Dict[str, Dict[Any, Any]], self.instance_commands[0].output)

        peers = command_output["vrfs"][vrf]["peers"]
        state_issue = _check_bgp_vrfs(command_output["vrfs"])

        if not state_issue and len(peers) == number:
            self.result.is_success()
        else:
            self.result.is_failure()
            if len(peers) != number:
                self.result.is_failure(f"Expecting {number} BGP peer in vrf {vrf} and got {len(peers)}")
            if state_issue:
                self.result.is_failure(f"The following IPv4 peers are not established: {state_issue}")


class VerifyBGPIPv6UnicastState(AntaTest):
    """
    Verifies all IPv6 unicast BGP sessions are established (for all VRF)
    and all BGP messages queues for these sessions are empty (for all VRF).

    * self.result = "skipped" if no BGP vrf are returned by the device
    * self.result = "success" if all IPv6 unicast BGP sessions are established (for all VRF)
                         and all BGP messages queues for these sessions are empty (for all VRF).
    * self.result = "failure" otherwise.
    """

    name = "VerifyBGPIPv6UnicastState"
    description = "Verifies all IPv6 unicast BGP sessions are established (for all VRF) and all BGP messages queues for these sessions are empty (for all VRF)."
    categories = ["routing", "bgp"]
    commands = [AntaTestCommand(command="show bgp ipv6 unicast summary vrf all")]

    @check_bgp_family_enable("ipv6")
    @AntaTest.anta_test
    def test(self) -> None:
        """Run VerifyBGPIPv6UnicastState validation"""

        command_output = cast(Dict[str, Dict[Any, Any]], self.instance_commands[0].output)

        state_issue = _check_bgp_vrfs(command_output["vrfs"])

        if not state_issue:
            self.result.is_success()
        else:
            self.result.is_failure(f"Some IPv4 Unicast BGP Peer are not up: {state_issue}")


class VerifyBGPEVPNState(AntaTest):
    """
    Verifies all EVPN BGP sessions are established (default VRF).

    * self.result = "skipped" if no BGP EVPN peers are returned by the device
    * self.result = "success" if all EVPN BGP sessions are established.
    * self.result = "failure" otherwise.
    """

    name = "VerifyBGPEVPNState"
    description = "Verifies all EVPN BGP sessions are established (default VRF)."
    categories = ["routing", "bgp"]
    commands = [AntaTestCommand(command="show bgp evpn summary")]

    @check_bgp_family_enable("evpn")
    @AntaTest.anta_test
    def test(self) -> None:
        """Run VerifyBGPEVPNState validation"""

        command_output = cast(Dict[str, Dict[Any, Any]], self.instance_commands[0].output)

        bgp_vrfs = command_output["vrfs"]

        peers = bgp_vrfs["default"]["peers"]
        non_established_peers = [peer for peer, peer_dict in peers.items() if peer_dict["peerState"] != "Established"]

        if not non_established_peers:
            self.result.is_success()
        else:
            self.result.is_failure(f"The following EVPN peers are not established: {non_established_peers}")


class VerifyBGPEVPNCount(AntaTest):
    """
    Verifies all EVPN BGP sessions are established (default VRF)
    and the actual number of BGP EVPN neighbors is the one we expect (default VRF).

    * self.result = "skipped" if the `number` parameter is missing
    * self.result = "success" if all EVPN BGP sessions are Established and if the actual
                         number of BGP EVPN neighbors is the one we expect.
    * self.result = "failure" otherwise.
    """

    name = "VerifyBGPEVPNCount"
    description = "Verifies all EVPN BGP sessions are established (default VRF) and the actual number of BGP EVPN neighbors is the one we expect (default VRF)."
    categories = ["routing", "bgp"]
    commands = [AntaTestCommand(command="show bgp evpn summary")]

    @check_bgp_family_enable("evpn")
    @AntaTest.anta_test
    def test(self, number: Optional[int] = None) -> None:
        """Run VerifyBGPEVPNCount validation"""
        if not number:
            self.result.is_skipped("VerifyBGPEVPNCount could not run because number was not supplied.")
            return

        command_output = cast(Dict[str, Dict[Any, Any]], self.instance_commands[0].output)

        peers = command_output["vrfs"]["default"]["peers"]
        non_established_peers = [peer for peer, peer_dict in peers.items() if peer_dict["peerState"] != "Established"]

        if not non_established_peers and len(peers) == number:
            self.result.is_success()
        else:
            self.result.is_failure()
            if len(peers) != number:
                self.result.is_failure(f"Expecting {number} BGP EVPN peers and got {len(peers)}")
            if non_established_peers:
                self.result.is_failure(f"The following EVPN peers are not established: {non_established_peers}")


class VerifyBGPRTCState(AntaTest):
    """
    Verifies all RTC BGP sessions are established (default VRF).

    * self.result = "skipped" if no BGP RTC peers are returned by the device
    * self.result = "success" if all RTC BGP sessions are established.
    * self.result = "failure" otherwise.
    """

    name = "VerifyBGPRTCState"
    description = "Verifies all RTC BGP sessions are established (default VRF)."
    categories = ["routing", "bgp"]
    commands = [AntaTestCommand(command="show bgp rtc-membership summary")]

    @check_bgp_family_enable("rtc")
    @AntaTest.anta_test
    def test(self) -> None:
        """Run VerifyBGPRTCState validation"""

        command_output = cast(Dict[str, Dict[Any, Any]], self.instance_commands[0].output)

        bgp_vrfs = command_output["vrfs"]

        peers = bgp_vrfs["default"]["peers"]
        non_established_peers = [peer for peer, peer_dict in peers.items() if peer_dict["peerState"] != "Established"]

        if not non_established_peers:
            self.result.is_success()
        else:
            self.result.is_failure(f"The following RTC peers are not established: {non_established_peers}")


class VerifyBGPRTCCount(AntaTest):
    """
    Verifies all RTC BGP sessions are established (default VRF)
    and the actual number of BGP RTC neighbors is the one we expect (default VRF).

    * self.result = "skipped" if the `number` parameter is missing
    * self.result = "success" if all RTC BGP sessions are Established and if the actual
                         number of BGP RTC neighbors is the one we expect.
    * self.result = "failure" otherwise.
    """

    name = "VerifyBGPRTCCount"
    description = "Verifies all RTC BGP sessions are established (default VRF) and the actual number of BGP RTC neighbors is the one we expect (default VRF)."
    categories = ["routing", "bgp"]
    commands = [AntaTestCommand(command="show bgp rtc-membership summary")]

    @check_bgp_family_enable("rtc")
    @AntaTest.anta_test
    def test(self, number: Optional[int] = None) -> None:
        """Run VerifyBGPRTCCount validation"""
        if not number:
            self.result.is_skipped("VerifyBGPRTCCount could not run because number was not supplied")
            return

        command_output = cast(Dict[str, Dict[Any, Any]], self.instance_commands[0].output)

        peers = command_output["vrfs"]["default"]["peers"]
        non_established_peers = [peer for peer, peer_dict in peers.items() if peer_dict["peerState"] != "Established"]

        if not non_established_peers and len(peers) == number:
            self.result.is_success()
        else:
            self.result.is_failure()
            if len(peers) != number:
                self.result.is_failure(f"Expecting {number} BGP RTC peers and got {len(peers)}")
            if non_established_peers:
                self.result.is_failure(f"The following RTC peers are not established: {non_established_peers}")
