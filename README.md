# ShadowTEAM Kex

ShadowTEAM Kex is a key exchange library that provides secure communication between peers using the Diffie-Hellman key exchange protocol. It allows peers to establish a shared secret key over an insecure network, which can then be used for secure communication.

<img src="https://github.com/user-attachments/assets/1940cfae-64de-4ec3-9599-a469e62c02e2" width="170">

<a href="https://github.com/DJStompZone/ShadowTeamKex/actions/workflows/github-code-scanning/codeql"><img src="https://github.com/DJStompZone/ShadowTeamKex/actions/workflows/github-code-scanning/codeql/badge.svg" width="120"></a> 

## Features

- Role negotiation: The library supports both initiator and listener roles, allowing peers to determine their roles dynamically based on a negotiation process.
- Diffie-Hellman key exchange: The library implements the Diffie-Hellman key exchange protocol to establish a shared secret key between peers.
- Key derivation: The library derives a full key from the shared secret key using the HKDF (HMAC-based Key Derivation Function) algorithm.
- Secure communication: Once the shared secret key is established, it can be used for secure communication between peers.

## Installation

To install ShadowTEAM Kex, you can use pip:
## Usage

Here is an example of how to use ShadowTEAM Kex:
In this example, the `DiffieHellmanExchangeManager` class is used to manage the key exchange process. The `start_exchange` method initiates the role negotiation and starts the key exchange process.

## Contributing

Contributions to ShadowTEAM Kex are welcome! If you find a bug or have a feature request, please open an issue on the GitHub repository. If you would like to contribute code, please fork the repository and submit a pull request.

## License

ShadowTEAM Kex is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
