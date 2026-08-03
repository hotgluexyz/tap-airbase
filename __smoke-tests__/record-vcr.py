from hotglue_smoke_test.vcr.tap import VCRTapTestRunner

class AirbaseTestRunner(VCRTapTestRunner):

    def module(self) -> str:
        return "tap_airbase"

    def launch(self):
        from tap_airbase.tap import TapAirbase
        TapAirbase.cli()


if __name__ == "__main__":
    AirbaseTestRunner.main()
